import mpuDriver as mpuD
import pyaudio
import math
import librosa
import time, datetime, statistics
import qwiic
import sys
import threading
import numpy as np
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Process
from multiprocessing import Pipe
from multiprocessing import Queue
import scipy.signal
import requests
import wave
import arguments as arg
import tflite_runtime.interpreter as tflite
from sklearn import preprocessing

_sample = False
_amount = 50
# tensorflow default float32, numpy default float64


class DataProcess(Process):
    def __init__(self, queue_mic, queue_acc):
        super(DataProcess, self).__init__()
        self.mpu = mpuD.MPU9250()
        self.queue_mic = queue_mic
        self.queue_acc = queue_acc

        # raw data placeholder
        self.mic_todo = [1 for i in range(7500)]
        self.acc_x_todo = [1 for i in range(500)]
        self.acc_y_todo = [1 for i in range(500)]
        self.acc_z_todo = [1 for i in range(500)]
        self.laser_todo = 0

    def mic_raw(self):
        # microphone init
        audio = pyaudio.PyAudio()
        chunk = 7500
        stream = audio.open(format=pyaudio.paInt16, rate=15000, channels=1, input=True, frames_per_buffer=chunk)
        stream.stop_stream()
        time.sleep(1)
        stream.start_stream()
        time.sleep(1)

        # microphone start

        if not _sample:
            print("INMP441: MIC Real Sample Start")
            while stream.is_active():
                start = time.time()
                stream_data = stream.read(chunk, exception_on_overflow=False)
                audio_data = np.frombuffer(stream_data, dtype=np.int16)
                self.mic_todo = audio_data
                # print('mic:', time.time()-start)

        if _sample:
            print(f"INMP441: MIC Train Sample Start {arg.activity}")
            index = burning_time = 0
            audio_frames = []
            while stream.is_active():
                start = time.time()
                stream_data = stream.read(chunk, exception_on_overflow=False)
                audio_frames.append(stream_data)
                burning_time = burning_time + time.time() - start
                index = index + 1
                if index % (2*_amount) == 0:
                    print('mic over sample:', burning_time / (2*_amount))
                    filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
                    wf = wave.open(f'../dataset/{arg.dataset}/mic/{arg.activity}/' + filename + f"-{arg.activity}" + '.wav', 'wb')
                    wf.setnchannels(1)
                    wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
                    wf.setframerate(15000)
                    wf.writeframes(b''.join(audio_frames))
                    wf.close()
                    return


    def mpu_acc_raw(self):
        time.sleep(2)

        # acc start
        if not _sample:
            print("MPU9250: ACC Real Sample Start")
            while True:
                start = time.time()
                acc = self.mpu.readAccel()
                del self.acc_x_todo[0]
                del self.acc_y_todo[0]
                del self.acc_z_todo[0]
                self.acc_x_todo.append(acc['x'])
                self.acc_y_todo.append(acc['y'])
                self.acc_z_todo.append(acc['z'])
                time.sleep(0.0006)
                # print('acc: ', time.time()-start)

        if _sample:
            print(f"MPU9250: ACC Train Sample Start {arg.activity}")
            index = burning_time = 0
            filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
            with open(f'../dataset/{arg.dataset}/acc/{arg.activity}/' + filename + f"-{arg.activity}" + '.txt', 'a') as f_acc:
                while True:
                    start = time.time()
                    accel = self.mpu.readAccel()
                    f_acc.write("{}, {}, {}, {}\r\n".format(index, accel['x'], accel['y'], accel['z']))
                    time.sleep(0.0006)
                    burning_time = burning_time + time.time() - start
                    index = index + 1
                    if index % (1000*_amount) == 0:
                        print('acc over sample:', burning_time/(1000*_amount))
                        return

    def laser(self):
        # laser init
        tof = qwiic.QwiicVL53L1X()
        if not tof.sensor_init():
            print("VL53L1X: Laser offline!\n")
        else:
            print("VL53L1X: Laser online!\n")
        tof.set_distance_mode(1)
        tof.set_timing_budget_in_ms(100)
        tof.stop_ranging()
        time.sleep(1)
        tof.start_ranging()
        time.sleep(1)

        # laser start
        last_distance = 0
        while tof.check_for_data_ready():
            start = time.time()
            distance = []
            for i in range(10):
                distance.append(tof.get_distance()/10)
                time.sleep(0.04)
            avgdistance = statistics.mean(distance)
            if last_distance - avgdistance > 0.2:
                self.laser_todo = 0
            elif last_distance - avgdistance < -0.2:
                self.laser_todo = 2
            else:
                self.laser_todo = 1
            last_distance = avgdistance
            # print("laser:", self.laser_todo, time.time() - start)
            # print(last_distance, self.laser_todo)
        tof.stop_ranging()

    def run(self):
        threads = []
        t1 = threading.Thread(target=self.mic_raw)
        threads.append(t1)
        t2 = threading.Thread(target=self.mpu_acc_raw)
        threads.append(t2)
        t3 = threading.Thread(target=self.laser)
        threads.append(t3)
        for t in threads:
            t.start()
        while True:
            if not self.queue_mic.full():
                start = time.time()
                data = {'mic': self.mic_todo}
                self.queue_mic.put(data)
            if not self.queue_acc.full():
                start = time.time()
                data = {'acc_x': self.acc_x_todo,
                        'acc_y': self.acc_y_todo,
                        'acc_z': self.acc_z_todo,
                        'laser': self.laser_todo}
                self.queue_acc.put(data)
            time.sleep(0.5)


class MicFeatureProcess(Process):
    def __init__(self, queue_in, queue_out):
        super(MicFeatureProcess, self).__init__()
        self.queue_in = queue_in
        self.queue_out = queue_out

    def run(self):
        scaler = preprocessing.StandardScaler()
        while True:
            if not self.queue_in.empty():
                start = time.time()
                result = self.queue_in.get()
                _, _, ps = scipy.signal.stft(result['mic'], fs=15000, nperseg=256, noverlap=32)
                mic_feature = scaler.fit_transform(abs(ps[1:]))
                self.queue_out.put(mic_feature)
                # print("mic_stft:", result['mic'][:10], time.time() - start)


class AccFeatureProcess(Process):
    def __init__(self, queue_in, queue_out):
        super(AccFeatureProcess, self).__init__()
        self.queue_in = queue_in
        self.queue_out = queue_out

    def run(self):
        scaler = preprocessing.StandardScaler()
        while True:
            if not self.queue_in.empty():
                start = time.time()
                result = self.queue_in.get()
                _, _, ps = scipy.signal.stft(result['acc_x'], fs=1000, nperseg=256, noverlap=160)
                acc_x_feature = scaler.fit_transform(abs(ps[1:]))
                _, _, ps = scipy.signal.stft(result['acc_y'], fs=1000, nperseg=256, noverlap=160)
                acc_y_feature = scaler.fit_transform(abs(ps[1:]))
                _, _, ps = scipy.signal.stft(result['acc_z'], fs=1000, nperseg=256, noverlap=160)
                acc_z_feature = scaler.fit_transform(abs(ps[1:]))
                laser_feature = [result['laser'] for i in range(128)]
                data = {'acc_x': acc_x_feature,
                        'acc_y': acc_y_feature,
                        'acc_z': acc_z_feature,
                        'laser': laser_feature}
                self.queue_out.put(data)
                # print("acc_stft:", result['acc_x'][:10], time.time() - start)


class RecoModelProcess(Process):
    def __init__(self, queue_mic_fea, queue_acc_fea):
        super(RecoModelProcess, self).__init__()
        self.queue_mic_fea = queue_mic_fea
        self.queue_acc_fea = queue_acc_fea

        # feature placeholder
        self.mic_feature = np.random.random((128, 35))
        self.acc_x_feature = np.random.random((128, 7))
        self.acc_y_feature = np.random.random((128, 7))
        self.acc_z_feature = np.random.random((128, 7))
        self.laser_feature = np.random.random((128, 1))

    def visulation(self, results):
        # 128 * 35 => 128 * 30
        mic_data = self.mic_feature[:, 5:]

        # 128 * 7  => 128 * 6
        acc_x_data = self.acc_x_feature[:, 1:]
        acc_y_data = self.acc_y_feature[:, 1:]
        acc_z_data = self.acc_z_feature[:, 1:]
        laser_data = self.laser_feature[0]

        # 128 * 30 => 64 * 30
        mic_data_tmp = []
        for i in range(0, 128, 2):
            mic_data_tmp.append(np.mean(mic_data[i:i+2], 0))

        # 64 * 30 => 6 * 64
        m = []
        mic_data = np.array(mic_data_tmp)
        for i in range(0, 30, 5):
            m.append(np.mean(mic_data[:, i:i+10], 1))

        # 128 * 6 => 64 * 6
        x = []
        y = []
        z = []
        for i in range(0, 128, 2):
            x.append(np.mean(acc_x_data[i:i+2], 0))
            y.append(np.mean(acc_y_data[i:i+2], 0))
            z.append(np.mean(acc_z_data[i:i+2], 0))

        x_tmp = []
        y_tmp = []
        z_tmp = []
        acc_x_data = np.transpose(np.array(x))
        acc_y_data = np.transpose(np.array(y))
        acc_z_data = np.transpose(np.array(z))
        for i in range(6):
            x_tmp.append(np.mean(acc_x_data[0:i+2], 0))
            y_tmp.append(np.mean(acc_y_data[0:i+2], 0))
            z_tmp.append(np.mean(acc_z_data[0:i+2], 0))
        x = x_tmp
        y = y_tmp
        z = z_tmp

        # 1 * 1 => 6 * 64
        l = np.array([laser_data for i in range(64 * 6)]).reshape(6, 64)

        # 64 * 6 => 6 * 64
        m = np.array(m) + 1
        x = np.array(x)
        y = np.array(y)
        z = np.array(z)

        m = m.reshape(-1).tolist()
        x = x.reshape(-1).tolist()
        y = y.reshape(-1).tolist()
        z = z.reshape(-1).tolist()
        l = l.reshape(-1).tolist()

        data = {'audio': m, 'x': x, 'y': y, 'z': z, 'l': l, 'active': results}
        requests.post(arg.url, json=data)

    def run(self):
        spin_interpreter = tflite.Interpreter(model_path="../tflite_model/bohr_spin.tflite")
        spin_interpreter.allocate_tensors()
        up_interpreter = tflite.Interpreter(model_path="../tflite_model/bohr_up.tflite")
        up_interpreter.allocate_tensors()
        down_interpreter = tflite.Interpreter(model_path="../tflite_model/bohr_down.tflite")
        down_interpreter.allocate_tensors()
        print(spin_interpreter.get_output_details())
        print(up_interpreter.get_output_details())
        print(down_interpreter.get_output_details())

        input_details = spin_interpreter.get_input_details()
        input_index = input_details[0]['index']
        # 0: 96, 1: 58, 2:68, 3:78, 4:88, 5:93

        mount = 0
        while True:
            pred_resutl = []
            start = time.time()
            if not self.queue_mic_fea.empty():
                result = self.queue_mic_fea.get()
                self.mic_feature = result
            if not self.queue_acc_fea.empty():
                result = self.queue_acc_fea.get()
                self.acc_x_feature = result['acc_x']
                self.acc_y_feature = result['acc_y']
                self.acc_z_feature = result['acc_z']
                self.laser_feature = result['laser']
                merge_feature = np.column_stack((self.mic_feature,
                                                self.acc_x_feature,
                                                self.acc_y_feature,
                                                self.acc_z_feature,
                                                self.laser_feature)).astype(dtype=np.float32).reshape(-1, 128, 57, 1)
                spin_interpreter.set_tensor(input_index, merge_feature)
                spin_interpreter.invoke()
                spin_output = spin_interpreter.get_tensor(96)
                if spin_output > 0.5:
                    pred_resutl.append('spin')
                    print(f"spin   : Y")
                else:
                    print(f"spin   : N")

                up_interpreter.set_tensor(input_index, merge_feature)
                up_interpreter.invoke()
                up_output = up_interpreter.get_tensor(93)
                if up_output > 0.5:
                    pred_resutl.append('up')
                    print(f"up     : Y")
                else:
                    print(f"up     : N")

                down_interpreter.set_tensor(input_index, merge_feature)
                down_interpreter.invoke()
                down_output = down_interpreter.get_tensor(93)
                if down_output > 0.5:
                    pred_resutl.append('down')
                    print(f"down   : Y")
                else:
                    print(f"down   : N")

                mount = mount + 1
                print(f"====={mount}========")
                start = time.time()
                self.visulation(pred_resutl)
                #rint(time.time()-start)


if __name__ == "__main__":
    queue_mic_raw = Queue()
    queue_acc_raw = Queue()
    queue_mic_fea = Queue()
    queue_acc_fea = Queue()
    d = DataProcess(queue_mic_raw, queue_acc_raw)
    m = MicFeatureProcess(queue_mic_raw, queue_mic_fea)
    a = AccFeatureProcess(queue_acc_raw, queue_acc_fea)
    r = RecoModelProcess(queue_mic_fea, queue_acc_fea)
    d.start()
    m.start()
    a.start()
    r.start()
