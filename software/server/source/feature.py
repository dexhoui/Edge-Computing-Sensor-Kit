#!/usr/bin/env python3.7.9
"""
Copyright © 2022 DUE TUL
@ desc  : This file is used to load raw data and exetract the feature for training.
@ author: BOHAO CHU
@ email : bohao.chu@qq.com
"""
import os
import time
import arguments as arg
import scipy.signal
import librosa
import numpy as np
import tensorflow as tf
from tqdm import tqdm
from sklearn.decomposition import PCA
from sklearn import preprocessing
import matplotlib.pyplot as plt


"""
@ name     : _float_feature
@ function : 
@ parameter: This file is used to load raw data and exetract the feature for training.
@ return   : BOHAO CHU
"""
def _float_feature(value):
    if not isinstance(value, list):
        value = [value]
    return tf.train.Feature(float_list=tf.train.FloatList(value=value))

"""
@ name     : _float_feature
@ function : 
@ parameter: This file is used to load raw data and exetract the feature for training.
@ return   : BOHAO CHU
"""
def _int64_feature(value):
    if not isinstance(value, list):
        value = [value]
    return tf.train.Feature(int64_list=tf.train.Int64List(value=value))


"""
@ name     : _float_feature
@ function : 
@ parameter: This file is used to load raw data and exetract the feature for training.
@ return   : BOHAO CHU
"""
def data_example(data, label):
    feature = {
        'data': _float_feature(data),
        'label': _int64_feature(label),
    }
    return tf.train.Example(features=tf.train.Features(feature=feature))


"""
@ name     : _float_feature
@ function : 
@ parameter: This file is used to load raw data and exetract the feature for training.
@ return   : BOHAO CHU
"""
def create_feature_tfrecord(list_path, train_save_path, test_save_path):
    mic_datas = []
    mic_labels = []

    acc_x_datas = []
    acc_y_datas = []
    acc_z_datas = []
    acc_labels = []

    laser_datas = []
    laser_labels = []

    mic_list_path = os.path.join(list_path, 'mic_list.txt')
    acc_list_path = os.path.join(list_path, 'acc_list.txt')
    laser_list_path = os.path.join(list_path, 'laser_list.txt')
    with open(mic_list_path, 'r+') as mic_all_paths, \
            open(acc_list_path, 'r+') as acc_all_paths, \
            open(laser_list_path, 'r+') as laser_all_paths:

        mic_files = mic_all_paths.readlines()
        for mic_file in mic_files:
            mic_path, mic_label = mic_file.replace('\n', '').split('\t')
            mic_stream, sr = librosa.load(mic_path, sr=15000, dtype=np.float32)
            for i in range(int(len(mic_stream) / 7500)):
                index = int(7500 * i)
                mic_datas.append(mic_stream[index:(index + 7500)])
                mic_labels.append(int(mic_label))

        acc_files = acc_all_paths.readlines()
        for acc_file in acc_files:
            acc_path, acc_label = acc_file.replace('\n', '').split('\t')
            _, x, y, z = np.loadtxt(acc_path, delimiter=',', unpack=True, dtype=np.float32)
            for i in range(int(len(x) / 500)):
                index = int(500 * i)
                data_x = x[index:(index + 500)]
                data_y = y[index:(index + 500)]
                data_z = z[index:(index + 500)]
                acc_x_datas.append(data_x)
                acc_y_datas.append(data_y)
                acc_z_datas.append(data_z)
                acc_labels.append(int(acc_label))

        laser_files = laser_all_paths.readlines()
        for laser_file in laser_files:
            laser_path, laser_label = laser_file.replace('\n', '').split('\t')
            x = np.loadtxt(laser_path, delimiter=',', unpack=True, dtype=np.float32)

            for i in range(len(x)):
                laser_datas.append(x[i])
                laser_labels.append(int(laser_label))

    scaler = preprocessing.StandardScaler()
    label = True
    with tf.io.TFRecordWriter(train_save_path) as train, tf.io.TFRecordWriter(test_save_path) as test:
        for i in tqdm(range(len(mic_datas))):
            if mic_labels[i] != acc_labels[i] != laser_labels[i]:
                return
            # MIC : Raw(7500,), Feature(60, 66)
            f, t, ps = scipy.signal.stft(mic_datas[i], fs=15000, nperseg=128, noverlap=16, boundary=None, padded=False)
            mic_feature = scaler.fit_transform(abs(ps[5:]))
            '''
            if label:
                label = False
                plt.pcolormesh(t, f, np.abs(ps))
                plt.colorbar()
                plt.ylabel('Frequency [Hz]')
                plt.xlabel('Time [sec]')
                plt.tight_layout()
                plt.show()
                time.sleep(5)
            '''
            # plt.imshow(mic_feature, cmap=plt.cm.gray, interpolation='nearest')
            # ACC : Raw(500, ), Feature(60, 8)
            _, _, ps = scipy.signal.stft(acc_x_datas[i], fs=1000, nperseg=128, noverlap=80, boundary=None, padded=False)
            acc_x_feature = scaler.fit_transform(abs(ps[5:]))
            _, _, ps = scipy.signal.stft(acc_y_datas[i], fs=1000, nperseg=128, noverlap=80, boundary=None, padded=False)
            acc_y_feature = scaler.fit_transform(abs(ps[5:]))
            _, _, ps = scipy.signal.stft(acc_z_datas[i], fs=1000, nperseg=128, noverlap=80, boundary=None, padded=False)
            acc_z_feature = scaler.fit_transform(abs(ps[5:]))

            # LASER : Raw(1, ), Feature(60, 1)
            laser_feature = [laser_datas[i] for j in range(60)]
            merge_feature = np.column_stack((mic_feature,
                                             acc_x_feature, acc_y_feature, acc_z_feature,
                                             laser_feature))
            merge_feature = merge_feature.reshape(-1).tolist()
            tf_example = data_example(merge_feature, int(mic_labels[i]))
            # split
            if i % 8 == 0:
                test.write(tf_example.SerializeToString())
            else:
                train.write(tf_example.SerializeToString())
        print("OK")


if __name__ == "__main__":
    create_feature_tfrecord(arg.data_list_path, arg.train_path, arg.test_path)
