import scipy
import numpy as np
from sklearn.preprocessing import scale
import scipy.signal as signal
import tflite_runtime.interpreter as tflite

def feature(audio_data, dis_data, mpu_x, mpu_y, mpu_z):
    f, t, ps = scipy.signal.stft(audio_data,
                                 fs=16000,
                                 nperseg=256,
                                 noverlap=32,
                                 boundary=None,
                                 padded=None)

    audio_feature = scale(abs(ps[1:, :]))

    # (1, )  (128, 1)
    laser_feature = [dis_data for j in range(128)]

    # mpu (1000, )  # (128, 6)
    f, t, ps = scipy.signal.stft(mpu_x,
                                 fs=1000,
                                 nperseg=256,
                                 noverlap=128,
                                 boundary=None,
                                 padded=None)
    mpu_x_feature = scale(abs(ps[1:, :]))
    f, t, ps = scipy.signal.stft(mpu_y,
                                 fs=1000,
                                 nperseg=256,
                                 noverlap=128,
                                 boundary=None,
                                 padded=None)
    mpu_y_feature = scale(abs(ps[1:, :]))
    f, t, ps = scipy.signal.stft(mpu_z,
                                 fs=1000,
                                 nperseg=256,
                                 noverlap=128,
                                 boundary=None,
                                 padded=None)
    mpu_z_feature = scale(abs(ps[1:, :]))

    merge_feature = np.column_stack((audio_feature,
                                     laser_feature,
                                     mpu_x_feature,
                                     mpu_y_feature,
                                     mpu_z_feature))

    return merge_feature

