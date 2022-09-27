import mpuDriver as mpuD
import pyaudio
import math
import librosa
import laserDriver as laserD
import time
import qwiic
import sys
import threading
import numpy as np
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Process
from multiprocessing import Pipe
import scipy.signal
mpu = mpuD.MPU9250()
time.sleep(3)
audio = pyaudio.PyAudio()
chunk = 3000
stream = audio.open(format=pyaudio.paInt16,
                    rate=15000,
                    channels=1,
                    input=True,
                    frames_per_buffer=chunk)
stream.stop_stream()
time.sleep(3)

acc_x_todo = [1 for i in range(2000)]
acc_y_todo = [1 for i in range(2000)]
acc_z_todo = [1 for i in range(2000)]

gyr_x_todo = [1 for i in range(2000)]
gyr_y_todo = [1 for i in range(2000)]
gyr_z_todo = [1 for i in range(2000)]

mic_todo = [1 for i in range(15000)]

def mpu_acc():
    global acc_x_todo
    global acc_y_todo
    global acc_z_todo
    print("MPU_ACC Start")
    while True:
        start = time.time()
        acc = mpu.readAccel()
        del acc_x_todo[0]
        del acc_y_todo[0]
        del acc_z_todo[0]
        acc_x_todo.append(acc['x'])
        acc_y_todo.append(acc['y'])
        acc_z_todo.append(acc['z'])
        #print("acc", time.time() - start)



# 1KHz
def mpu_gyr():
    global gyr_x_todo
    global gyr_y_todo
    global gyr_z_todo
    while True:
        start = time.time()
        gyr = mpu.readGyro()
        del gyr_x_todo[0]
        del gyr_y_todo[0]
        del gyr_z_todo[0]
        gyr_x_todo.append(gyr['x'])
        gyr_y_todo.append(gyr['y'])
        gyr_z_todo.append(gyr['z'])
        #print("gyr:", time.time()-start)


# 20Hz = 20Hz * 1
def mpu_mag():
    mag_x_data_real = [0 for i in range(10)]
    mag_y_data_real = [0 for i in range(10)]
    mag_z_data_real = [0 for i in range(10)]
    while True:
        start = time.time()
        time.sleep(0.1)
        mag = mpu.readMagnet()
        del mag_x_data_real[0]
        del mag_y_data_real[0]
        del mag_z_data_real[0]
        mag_x_data_real.append(mag['x'])
        mag_y_data_real.append(mag['y'])
        mag_z_data_real.append(mag['z'])


# 10Hz = 10Hz * 1
def laser():
    tof = qwiic.QwiicVL53L1X()
    if tof.sensor_init() is not None:
        print("VL53L1X: Laser offline!\n")
    else:
        print("VL53L1X: Laser online!\n")
    tof.set_distance_mode(1)
    tof.set_timing_budget_in_ms(100)
    tof.start_ranging()
    time.sleep(0.5)
    while tof.check_for_data_ready():
        start = time.time()
        time.sleep(0.1)
        l = tof.get_distance()
        #print("laser:", time.time() - start)
    tof.stop_ranging()


# 15KHz = 10Hz * 1500
def mic():
    global mic_todo
    print("INMP441: MIC STAR\n")
    stream.start_stream()
    # plot
    while stream.is_active():
        start = time.time()
        stream_data = stream.read(chunk, exception_on_overflow=False)
        del mic_todo[:3000]
        mic_todo.extend(np.frombuffer(stream_data, dtype=np.int16))
    stream.stop_stream()


def stft_acc():
    global acc_x_todo
    global acc_y_todo
    global acc_z_todo
    while True:
        start = time.time()
        #scipy.signal.stft(acc_x_todo, fs=2000, nperseg=256, noverlap=32, boundary=None, padded=None)
        _, _, ps = scipy.signal.stft(acc_y_todo, fs=2000,
                                     window='hann',
                                     nperseg=256, noverlap=32, boundary=None, padded=None, return_onesided=True)
        scipy.signal.stft(acc_z_todo, fs=2000, nperseg=256, noverlap=32, boundary=None, padded=None)
        scipy.signal.stft(acc_z_todo, fs=2000, nperseg=256, noverlap=32, boundary=None, padded=None)
        #print("acc_stft:", time.time()-start)
        time.sleep(1)

def stft_gyr():
    global gyr_x_todo
    global gyr_y_todo
    global gyr_z_todo
    while True:
        start = time.time()
        scipy.signal.stft(gyr_x_todo, fs=2000, nperseg=256, noverlap=32, boundary=None, padded=None)
        scipy.signal.stft(gyr_y_todo, fs=2000, nperseg=256, noverlap=32, boundary=None, padded=None)
        scipy.signal.stft(gyr_z_todo, fs=2000, nperseg=256, noverlap=32, boundary=None, padded=None)
        #print("gyr_stft:", gyr_x_todo[:10], time.time()-start)
        time.sleep(1)

def stft_mic():
    global mic_todo
    while True:
        start = time.time()
        f, t, zxx = scipy.signal.stft(mic_todo,
                                     fs=15000,
                                     window='hann',
                                     nperseg=512, noverlap=256, boundary=None, padded=None)
        print("mic_stft:", zxx.shape, mic_todo[:5], time.time() - start)


def data_process_multi_thread():
    threads = []
    t1 = threading.Thread(target=mpu_acc)
    threads.append(t1)
    t2 = threading.Thread(target=mpu_gyr)
    threads.append(t2)
    t3 = threading.Thread(target=mpu_mag)
    threads.append(t3)
    t4 = threading.Thread(target=laser)
    threads.append(t4)
    t5 = threading.Thread(target=mic)
    threads.append(t5)
    t6 = threading.Thread(target=stft_acc)
    threads.append(t6)
    t7 = threading.Thread(target=stft_gyr)
    threads.append(t7)
    t8 = threading.Thread(target=stft_mic)
    threads.append(t8)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def son_process(pipe):
    _out_pipe, _in_pipe = pipe
    _in_pipe.close()
    mic_todo = [1 for i in range(15000)]
    while True:
        try:
            mic_todo = _out_pipe.recv()
            start = time.time()
            f, t, zxx = scipy.signal.stft(mic_todo,
                                          fs=15000,
                                          window='hann',
                                          nperseg=512, noverlap=256, boundary=None, padded=None)
            print("sub:", mic_todo[:5])
            time.sleep(0.1)
            #print("mic2_stft:", zxx.shape, mic_todo[:5], time.time() - start)
        except EOFError:
            """ 当out_pipe接受不到输出的时候且输入被关闭的时候，会抛出EORFError，可以捕获并且退出子进程 """
            break





out_pipe, in_pipe = Pipe(True)
son1_p = Process(target=son_process, args=((out_pipe, in_pipe),))
son1_p.start()
son2_p = Process(target= data_process_multi_thread)
son2_p.start()
out_pipe.close()
while True:
    print("mian:", mic_todo[:5])
    in_pipe.send(mic_todo)
in_pipe.close()
son1_p.join()
son2_p.join()
print("主进程结束")

son1_p.join()
son2_p.join()
print("主进程结束")
