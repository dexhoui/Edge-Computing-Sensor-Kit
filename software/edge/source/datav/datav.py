import os, sys, time
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.dirname(SCRIPT_DIR)
ROOT_DIR = os.path.dirname(SOURCE_DIR)
sys.path.append(SOURCE_DIR)
sys.path.append(ROOT_DIR)
import numpy as np
import requests
import arguments as arg
import matplotlib.pyplot as plt


# def datav(mic_data, acc_x_data, acc_y_data, acc_z_data, laser_data, results):
def datasave(name, data):
    plt.plot(range(len(data)), data)
    plt.savefig(f"{ROOT_DIR}/assets/images/data/{name}-data-{len(data)}-{time.time()}.png")
    plt.close()


def featurev(mic_feature, acc_x_feature, acc_y_feature, acc_z_feature, laser_feature, results, laser_data, eye_data, color_data, bme_data, mag_data):
    # 60 * 66 => 60 * 60
    mic_data = mic_feature[:, 6:]
    # 60 * 60 => 6 * 60
    m = []
    for i in range(0, 60, 10):
        m.append(np.mean(mic_data[:, i:i + 10], 1))
    # 6 * 60 => 6 * 64
    t = np.zeros((6, 4))
    m = np.concatenate((t, np.array(m)), axis=1)

    # 60 * 8  => 6 * 60
    acc_x_data = np.transpose(acc_x_feature[:, 2:])
    acc_y_data = np.transpose(acc_y_feature[:, 2:])
    acc_z_data = np.transpose(acc_z_feature[:, 2:])

    # 6 * 60 => 6 * 64
    t = np.zeros((6, 4))
    x = np.concatenate((t, acc_x_data), axis=1)
    y = np.concatenate((t, acc_y_data), axis=1)
    z = np.concatenate((t, acc_z_data), axis=1)

    # 1 * 1 => 6 * 64
    l = laser_feature

    # 8*8 => 6*8
    e = np.array(eye_data).reshape(8, 8)[:, 1:7].transpose().reshape(-1).tolist()

    m = (2*m).reshape(-1).tolist()
    x = x.reshape(-1).tolist()
    y = y.reshape(-1).tolist()
    z = z.reshape(-1).tolist()

    data = {'m': m, 'x': x, 'y': y, 'z': z, 'l': l, 'ld': laser_data, 'e': e, 'color': color_data, 'bme': bme_data, 'mag':mag_data, 'activity': results}
    try:
        feedback = requests.get(arg.url, json=data, timeout=20)
        # print(feedback.text, results)
    except requests.exceptions.ConnectionError:
        print('ConnectionError')
        time.sleep(3)
    except requests.exceptions.ChunkedEncodingError:
        print('ChunkedEncodingError')