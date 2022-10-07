import time, os, sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.dirname(SCRIPT_DIR)
ROOT_DIR = os.path.dirname(SOURCE_DIR)
sys.path.append(SOURCE_DIR)
sys.path.append(ROOT_DIR)
import scipy.signal
from sklearn import preprocessing
import matplotlib.pyplot as plt
import numpy as np



def normalization(data):
    _range = np.max(data) - np.min(data)
    return (data - np.min(data)) / _range

def featuresave(name, data):
    plt.imshow(data, origin='lower', vmin=-3, vmax=7)
    plt.savefig(f"{ROOT_DIR}/assets/images/feature/{name}-feature-{time.time()}.png")
    plt.close()


def micfeature(mic_data):
    scaler = preprocessing.StandardScaler()
    _, _, ps = scipy.signal.stft(mic_data, fs=15000, nperseg=128, noverlap=16, boundary=None, padded=False)  # 65,66
    mic_feature = scaler.fit_transform(abs(ps[5:]))  # 60, 66
    return mic_feature


def accfreature(acc_x_data, acc_y_data, acc_z_data):
    scaler = preprocessing.StandardScaler()
    _, _, ps = scipy.signal.stft(acc_x_data, fs=1000, nperseg=128, noverlap=80, boundary=None, padded=False)  # 65, 8
    acc_x_feature = scaler.fit_transform(abs(ps[5:]))  # 60, 8
    _, _, ps = scipy.signal.stft(acc_y_data, fs=1000, nperseg=128, noverlap=80, boundary=None, padded=False)
    acc_y_feature = scaler.fit_transform(abs(ps[5:]))
    _, _, ps = scipy.signal.stft(acc_z_data, fs=1000, nperseg=128, noverlap=80, boundary=None, padded=False)
    acc_z_feature = scaler.fit_transform(abs(ps[5:]))
    return acc_x_feature, acc_y_feature, acc_z_feature
