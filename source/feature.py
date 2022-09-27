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
import pywt
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
def create_feature_tfrecord(mic_list_path, acc_list_path, laser_list_path,
                            train_save_path, test_save_path):
    mic_datas = []
    mic_labels = []

    acc_x_datas = []
    acc_y_datas = []
    acc_z_datas = []
    acc_labels = []

    laser_datas = []
    laser_labels = []

    with open(mic_list_path, 'r+') as mic_all_paths, \
            open(acc_list_path, 'r+') as acc_all_paths, \
            open(laser_list_path, 'r+') as laser_all_paths:

        mic_files = mic_all_paths.readlines()
        for mic_file in mic_files:
            mic_path, mic_label = mic_file.replace('\n', '').split('\t')
            mic_stream, sr = librosa.load(mic_path, sr=15000, dtype=np.float32)
            for i in range(int(len(mic_stream) / 3750)):
                index = int(3750 * i)
                mic_datas.append(mic_stream[index:(index + 3750)])
                mic_labels.append(int(mic_label))

        acc_files = acc_all_paths.readlines()
        for acc_file in acc_files:
            acc_path, acc_label = acc_file.replace('\n', '').split('\t')
            _, x, y, z = np.loadtxt(acc_path, delimiter=',', unpack=True, dtype=np.float32)
            for i in range(int(len(x) / 250)):
                index = int(250 * i)
                data_x = x[index:(index + 250)]
                data_y = y[index:(index + 250)]
                data_z = z[index:(index + 250)]
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
    with tf.io.TFRecordWriter(train_save_path) as train, tf.io.TFRecordWriter(test_save_path) as test:
        for i in tqdm(range(len(mic_datas))):
            if mic_labels[i] != acc_labels[i] != laser_labels[i]:
                return
            # MIC : Raw(7500,), Feature(64, 41)
            _, _, ps = scipy.signal.stft(mic_datas[i], fs=15000, nperseg=128, noverlap=32)
            mic_feature = scaler.fit_transform(abs(ps[1:]))

            # ACC : Raw(500, ), Feature(64, 5)
            _, _, ps = scipy.signal.stft(acc_x_datas[i], fs=1000, nperseg=128)
            acc_x_feature = scaler.fit_transform(abs(ps[1:]))
            _, _, ps = scipy.signal.stft(acc_y_datas[i], fs=1000, nperseg=128)
            acc_y_feature = scaler.fit_transform(abs(ps[1:]))
            _, _, ps = scipy.signal.stft(acc_z_datas[i], fs=1000, nperseg=128)
            acc_z_feature = scaler.fit_transform(abs(ps[1:]))

            # LASER : Raw(1, ), Feature(64, 1)
            laser_feature = [laser_datas[i] for j in range(64)]

            merge_feature = np.column_stack((mic_feature,
                                             acc_x_feature, acc_y_feature, acc_z_feature,
                                             laser_feature))
            merge_feature = merge_feature.reshape(-1).tolist()
            tf_example = data_example(merge_feature, int(mic_labels[i]))
            # split
            if i % 9 == 0:
                test.write(tf_example.SerializeToString())
            else:
                train.write(tf_example.SerializeToString())
        print("OK")


"""
@ name     : _float_feature
@ function : 
@ parameter: This file is used to load raw data and exetract the feature for training.
@ return   : BOHAO CHU
"""
def get_mic_data_list(mic_path, list_path):
    mic_class_dir = os.listdir(mic_path)
    with open(list_path, 'w') as f_mic:
        for i in range(len(mic_class_dir)):
            sound_dir = os.listdir(os.path.join(mic_path, mic_class_dir[i]))
            for sound_file in sound_dir:
                sound_file_path = os.path.join(mic_path, mic_class_dir[i], sound_file)
                f_mic.write('%s\t%d\n' % (sound_file_path, i))
            print("mic：%d/%d  %d" % (i + 1, len(mic_class_dir), len(sound_dir)))


"""
@ name     : _float_feature
@ function : 
@ parameter: This file is used to load raw data and exetract the feature for training.
@ return   : BOHAO CHU
"""
def get_acc_data_list(acc_path, list_path):
    acc_class_dir = os.listdir(acc_path)
    with open(list_path, 'w') as f_acc:
        for i in range(len(acc_class_dir)):
            acc_dir = os.listdir(os.path.join(acc_path, acc_class_dir[i]))
            for acc_file in acc_dir:
                acc_file_path = os.path.join(acc_path, acc_class_dir[i], acc_file)
                f_acc.write('%s\t%d\n' % (acc_file_path, i))
            print("acc：%d/%d  %d" % (i + 1, len(acc_class_dir), len(acc_dir)))


"""
@ name     : _float_feature
@ function : 
@ parameter: This file is used to load raw data and exetract the feature for training.
@ return   : BOHAO CHU
"""
def get_gyr_data_list(gyr_path, list_path):
    gyr_class_dir = os.listdir(gyr_path)
    with open(list_path, 'w') as f_gyr:
        for i in range(len(gyr_class_dir)):
            gyr_dir = os.listdir(os.path.join(gyr_path, gyr_class_dir[i]))
            for gyr_file in gyr_dir:
                gyr_file_path = os.path.join(gyr_path, gyr_class_dir[i], gyr_file)
                f_gyr.write('%s\t%d\n' % (gyr_file_path, i))
            print("gyr：%d/%d  %d" % (i + 1, len(gyr_class_dir), len(gyr_dir)))


"""
@ name     : _float_feature
@ function : 
@ parameter: This file is used to load raw data and exetract the feature for training.
@ return   : BOHAO CHU
"""
def get_laser_data_list(laser_path, list_path):
    laser_class_dir = os.listdir(laser_path)
    with open(list_path, 'w') as f_mpu:
        for i in range(len(laser_class_dir)):
            laser_dir = os.listdir(os.path.join(laser_path, laser_class_dir[i]))
            for laser_file in laser_dir:
                laser_file_path = os.path.join(laser_path, laser_class_dir[i], laser_file)
                f_mpu.write('%s\t%d\n' % (laser_file_path, i))
            print("laser  ：%d/%d  %d" % (i + 1, len(laser_class_dir), len(laser_dir)))


if __name__ == "__main__":
    get_mic_data_list(
        f'dataset/data/{arg.database}/{arg.activity}/mic',
        f'dataset/list/{arg.database}/{arg.activity}/mic_data_list.txt'
    )

    get_acc_data_list(
        f'dataset/data/{arg.database}/{arg.activity}/acc',
        f'dataset/list/{arg.database}/{arg.activity}/acc_data_list.txt'
    )

    get_laser_data_list(
        f'dataset/data/{arg.database}/{arg.activity}/laser',
        f'dataset/list/{arg.database}/{arg.activity}/laser_data_list.txt'
    )

    create_feature_tfrecord(
        f'dataset/list/{arg.database}/{arg.activity}/mic_data_list.txt',
        f'dataset/list/{arg.database}/{arg.activity}/acc_data_list.txt',
        f'dataset/list/{arg.database}/{arg.activity}/laser_data_list.txt',
        f'dataset/tfrecords/{arg.database}/{arg.activity}/train.tfrecord',
        f'dataset/tfrecords/{arg.database}/{arg.activity}/test.tfrecord'
    )
