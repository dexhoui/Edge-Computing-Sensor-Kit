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
import wave
import arguments as arg
import tflite_runtime.interpreter as tflite
from sklearn import preprocessing

__sample__ = False
__samele_amount__ = 100

# tensorflow default float32, numpy default float64

class DataProcess(Process):
    def __init__(self, queue):
        super(DataProcess, self).__init__()
        self.mpu = mpuD.MPU9250()
        self.queue = queue

        self.mic_todo = [1 for i in range(15000)]

        self.acc_x_todo = [1 for i in range(2000)]
        self.acc_y_todo = [1 for i in range(2000)]
        self.acc_z_todo = [1 for i in range(2000)]

        self.gyr_x_todo = [1 for i in range(2000)]
        self.gyr_y_todo = [1 for i in range(2000)]
        self.gyr_z_todo = [1 for i in range(2000)]

        self.mag_x_todo = [0 for i in range(10)]
        self.mag_y_todo = [0 for i in range(10)]
        self.mag_z_todo = [0 for i in range(10)]

        self.laser_todo = 0
        self.humid_todo = [0 for i in range(10)]
        self.tempe_todo = [0 for i in range(10)]
        self.press_todo = [0 for i in range(10)]
        self.altit_todo = [0 for i in range(10)]

    def mic(self):
        audio = pyaudio.PyAudio()
        chunk = 3000
        stream = audio.open(format=pyaudio.paInt16,
                            rate=15000,
                            channels=1,
                            input=True,
                            frames_per_buffer=chunk)
        stream.stop_stream()
        print("INMP441: MIC Online")
        time.sleep(1)
        stream.start_stream()
        time.sleep(2)
        if not __sample__:
            while stream.is_active():
                start = time.time()
                stream_data = stream.read(chunk, exception_on_overflow=False)
                audio_data = np.frombuffer(stream_data, dtype=np.int16)
                del self.mic_todo[:chunk]
                self.mic_todo.extend(audio_data)
                # print("MIC:", time.time() - start)
        else:
            amount = 1
            audio_frames = []
            times=0
            while stream.is_active():
                start = time.time()
                stream_data = stream.read(chunk, exception_on_overflow=False)
                audio_frames.append(stream_data)
                #print("MIC:", len(audio_frames), time.time() - start)
                times = times + (time.time()-start)
                if amount % 500 == 0:
                    print(times/500)
                    filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
                    wf = wave.open(f'../dataset/mic/{arg.activity}/'+ filename + f"-{arg.activity}" + '.wav', 'wb')
                    wf.setnchannels(1)
                    wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
                    wf.setframerate(15000)
                    wf.writeframes(b''.join(audio_frames))
                    wf.close()
                    audio_frames = []
                    amount = 1
                    return
                amount = amount + 1

        stream.stop_stream()

    def mpu_acc(self):
        # 0.00033
        print("MPU9250: ACC Online")
        time.sleep(3)
        if not __sample__:
            amount = 1
            times = 0
            while True:
                start = time.time()
                acc = self.mpu.readAccel()
                del self.acc_x_todo[0]
                del self.acc_y_todo[0]
                del self.acc_z_todo[0]
                self.acc_x_todo.append(acc['x'])
                self.acc_y_todo.append(acc['y'])
                self.acc_z_todo.append(acc['z'])
                times = times + time.time() - start
                if amount % 20 == 0:
                    #print(times/20)
                    times = 0
                amount = amount + 1
                # 0.00033 = 3000 = 3K
                #print("acc", time.time() - start)
        else:
            amount = 1
            times = 0
            filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
            with open(f'../dataset/acc/{arg.activity}/' + filename + f"-{arg.activity}" + '.txt', 'a') as f_acc:
                while True:
                    start = time.time()
                    accel = self.mpu.readAccel()
                    f_acc.write("{}, {}, {}, {}\r\n".format(amount, accel['x'], accel['y'], accel['z']))
                    times = times + time.time() - start
                    if amount % 200000 == 0:
                        #print(times/200000)
                        times = 0
                        return
                    amount = amount + 1
                    # 0.0005 = 2000 = 2K
                    #print("acc", time.time() - start)
    '''
    def mpu_gyr(self):
        # 0.0004
        print("MPU9250: GYR Online")
        time.sleep(3)
        if not __sample__:
            amount = 1
            times = 0
            while True:
                start = time.time()
                gyr = self.mpu.readGyro()
                del self.gyr_x_todo[0]
                del self.gyr_y_todo[0]
                del self.gyr_z_todo[0]
                self.gyr_x_todo.append(gyr['x'])
                self.gyr_y_todo.append(gyr['y'])
                self.gyr_z_todo.append(gyr['z'])
                times = times + time.time() - start
                if amount % 20 == 0:
                    # print(times/20)
                    times = 0
                amount = amount + 1
                # 0.0004 = 2500 = 2.5K
                # print("gyr:", time.time()-start)
        else:
            amount = 1
            times = 0
            filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
            with open(f'../dataset/gyr/{arg.activity}/' + filename + f"-{arg.activity}" + '.txt', 'a') as f_gyr:
                while True:
                    start = time.time()
                    gyr = self.mpu.readGyro()
                    f_gyr.write("{}, {}, {}, {}\r\n".format(amount, gyr['x'], gyr['y'], gyr['z']))
                    times = times + time.time()-start
                    if amount % 200000 == 0:
                        print(times/200000)
                        times = 0
                        return
                    amount = amount + 1
                    # 0.0005 = 2000 = 2K
                    #print("gyr", time.time() - start)

    def mpu_mag(self):
        # 0.12
        print("MPU9250: MAG Online")
        time.sleep(3)
        while True:
            start = time.time()
            time.sleep(0.1)
            mag = self.mpu.readMagnet()
            del self.mag_x_todo[0]
            del self.mag_y_todo[0]
            del self.mag_z_todo[0]
            self.mag_x_todo.append(mag['x'])
            self.mag_y_todo.append(mag['y'])
            self.mag_z_todo.append(mag['z'])
            # print("mag:", time.time()-start)
    '''

    def laser(self):
        # 0.11
        tof = qwiic.QwiicVL53L1X()
        if not tof.sensor_init():
            print("VL53L1X: Laser offline!\n")
        else:
            print("VL53L1X: Laser online!\n")
        tof.set_distance_mode(1)
        tof.set_timing_budget_in_ms(100)
        tof.stop_ranging()
        time.sleep(1.5)
        tof.start_ranging()
        time.sleep(1.5)
        last_distance = 0
        while tof.check_for_data_ready():
            start = time.time()
            distance = []
            for i in range(15):
                distance.append(tof.get_distance()/10)
            avgdistance = statistics.mean(distance)
            if last_distance - avgdistance > 0.2:
                self.laser_todo = 0
            elif last_distance - avgdistance < -0.2:
                self.laser_todo = 2
            else:
                self.laser_todo = 1
            last_distance = avgdistance
            #print("laser:", self.laser_todo, time.time() - start)
        tof.stop_ranging()

    '''
    def htpa(self):
        # 0.11
        htpa = qwiic.QwiicBme280(address=0x76)
        if htpa.connected == False:
            print("BME280 : device isn't connected to the system. Please check your connection", file=sys.stderr)
            return
        else:
            print("BME280 : HTPA Online")
        htpa.begin()
        time.sleep(3)
        while True:
            start = time.time()
            h = htpa.humidity
            t = htpa.get_temperature_celsius
            p = htpa.pressure
            a = htpa.altitude_feet
            del self.humid_todo[0]
            del self.tempe_todo[0]
            del self.press_todo[0]
            del self.altit_todo[0]
            self.humid_todo.append(h)
            self.tempe_todo.append(t)
            self.press_todo.append(p)
            self.altit_todo.append(a)
            time.sleep(0.1)
            #print("HTPA:", time.time()-start)
    '''

    def run(self):
        threads = []
        t1 = threading.Thread(target=self.mic)
        threads.append(t1)
        t2 = threading.Thread(target=self.mpu_acc)
        threads.append(t2)
        #t3 = threading.Thread(target=self.mpu_gyr)
        #threads.append(t3)
        #t4 = threading.Thread(target=self.mpu_mag)
        #threads.append(t4)
        t5 = threading.Thread(target=self.laser)
        threads.append(t5)
        #t6 = threading.Thread(target=self.htpa)
        #threads.append(t6)
        for t in threads:
            t.start()
        while True:
            if not self.queue.full():
                start = time.time()
                data = {'mic': self.mic_todo,
                        'laser': self.laser_todo,
                        'acc_x': self.acc_x_todo,
                        'acc_y': self.acc_y_todo,
                        'acc_z': self.acc_z_todo}
                self.queue.put(data)
                time.sleep(0.2)
                # 0.002
                # print("S:", time.time()-start)


class FeatureProcess(Process):
    def __init__(self, queue):
        super(FeatureProcess, self).__init__()
        self.queue = queue

        self.mic_todo = [1 for i in range(15000)]
        self.acc_x_todo = [1 for i in range(2000)]
        self.acc_y_todo = [1 for i in range(2000)]
        self.acc_z_todo = [1 for i in range(2000)]

        self.gyr_x_todo = [1 for i in range(2000)]
        self.gyr_y_todo = [1 for i in range(2000)]
        self.gyr_z_todo = [1 for i in range(2000)]

        self.mag_x_todo = [1 for i in range(2000)]
        self.mag_y_todo = [1 for i in range(2000)]
        self.mag_z_todo = [1 for i in range(2000)]

        self.laser_todo = 1

        self.mic_feature = np.random.random((128, 68))
        self.acc_x_feature = np.random.random((128, 22))
        self.acc_y_feature = np.random.random((128, 22))
        self.acc_z_feature = np.random.random((128, 22))
        self.laser_feature = np.random.random((128, 1))

    def stft_mic(self):
        scaler = preprocessing.StandardScaler()
        while True:
            start = time.time()
            _, _, ps = scipy.signal.stft(self.mic_todo, fs=15000, nperseg=256, noverlap=32)
            self.mic_feature = scaler.fit_transform(abs(ps[1:]))
            self.laser_feature = [self.laser_todo for i in range(128)]
            time.sleep(0.2)
            # print("mic_stft:", self.mic_feature, time.time() - start)


    def stft_acc(self):
        scaler = preprocessing.StandardScaler()
        while True:
            start = time.time()
            # scipy.signal.stft(acc_x_todo, fs=2000, nperseg=256, noverlap=32, boundary=None, padded=None)
            _, _, ps = scipy.signal.stft(self.acc_x_todo, fs=2000, nperseg=256, noverlap=160)
            self.acc_x_feature = scaler.fit_transform(abs(ps[1:]))
            _, _, ps = scipy.signal.stft(self.acc_y_todo, fs=2000, nperseg=256, noverlap=160)
            self.acc_y_feature = scaler.fit_transform(abs(ps[1:]))
            _, _, ps = scipy.signal.stft(self.acc_z_todo, fs=2000, nperseg=256, noverlap=160)
            self.acc_z_feature = scaler.fit_transform(abs(ps[1:]))
            time.sleep(0.2)
            #print("acc_stft:", self.acc_x_feature.shape, time.time()-start)

    def model_rec(self):
        on_interpreter = tflite.Interpreter(model_path="../tflite_model/bottom.tflite")
        on_interpreter.allocate_tensors()
        print(on_interpreter.get_output_details())
        spin_interpreter = tflite.Interpreter(model_path="../tflite_model/spin.tflite")
        spin_interpreter.allocate_tensors()
        print(spin_interpreter.get_output_details())
        left_interpreter = tflite.Interpreter(model_path="../tflite_model/left.tflite")
        left_interpreter.allocate_tensors()
        print(left_interpreter.get_output_details())
        right_interpreter = tflite.Interpreter(model_path="../tflite_model/right.tflite")
        right_interpreter.allocate_tensors()
        print(right_interpreter.get_output_details())
        bottom_interpreter = tflite.Interpreter(model_path="../tflite_model/bottom.tflite")
        bottom_interpreter.allocate_tensors()
        print(bottom_interpreter.get_output_details())
        input_details = on_interpreter.get_input_details()
        output_details = on_interpreter.get_output_details()
        input_index = input_details[0]['index']
        output_index = output_details[1]['index']
        on_flag = 'N'
        spin_flag = 'N'
        left_flag = 'N'
        right_flag = "N"
        while True:
            start = time.time()
            #print(self.laser_feature)
            merge_feature = np.column_stack((self.mic_feature, self.acc_x_feature, self.acc_y_feature,
                                             self.acc_z_feature, self.acc_x_feature, self.acc_y_feature,
                                             self.acc_z_feature, self.laser_feature)).astype(dtype=np.float32).reshape(-1, 128, 201, 1)

            on_interpreter.set_tensor(input_index, merge_feature)
            on_interpreter.invoke()
            on_output = on_interpreter.get_tensor(output_index)
            if on_output > 0.65:
                on_flag = 'Y'
                #print(f"on     Y : {on_output[0][0]}")
            else:
                on_flag = 'N'
                #print(f"on     N : {on_output[0][0]}")
            '''
            spin_interpreter.set_tensor(input_index, merge_feature)
            spin_interpreter.invoke()
            spin_output = spin_interpreter.get_tensor(output_index)
            if spin_output > 0.65:
                spin_flag = 'Y'
                #print(f"spin   Y : {spin_output[0][0]}")
            else:
                spin_flag = 'N'
                #print(f"spin   N : {spin_output[0][0]}")

            left_interpreter.set_tensor(input_index, merge_feature)
            left_interpreter.invoke()
            left_output = left_interpreter.get_tensor(output_index)
            if left_output > 0.65:
                left_flag = 'Y'
                #print(f"left   Y : {left_output[0][0]}")
            else:
                left_flag = "N"
                #print(f"left   N : {left_output[0][0]}")

            right_interpreter.set_tensor(input_index, merge_feature)
            right_interpreter.invoke()
            right_output = right_interpreter.get_tensor(output_index)
            if right_output > 0.65:
                right_flag = "Y"
                #print(f"right  Y : {right_output[0][0]}")
            else:
                right_flag = "N"
                #print(f"right  N : {right_output[0][0]}")

            bottom_interpreter.set_tensor(input_index, merge_feature)
            bottom_interpreter.invoke()
            bottom_output = bottom_interpreter.get_tensor(output_index)
            if bottom_output > 0.65:
                bottom_flag = 'Y'
                #print(f"bottom Y : {bottom_output[0][0]}")
            else:
                bottom_flag = "N"
                #print(f"bottom N : {bottom_output[0][0]}")
            '''
            print(f"on  :{on_flag}:{on_output[0][0]}")
            #print(f"spin:{spin_flag}:{spin_output[0][0]}")
            #print(f"left:{left_flag}:{left_output[0][0]}")
            print(f"=======================")


    def run(self):
        threads = []
        t1 = threading.Thread(target=self.stft_mic)
        threads.append(t1)
        t2 = threading.Thread(target=self.stft_acc)
        threads.append(t2)
        t3 = threading.Thread(target=self.model_rec)
        threads.append(t3)
        for t in threads:
            t.start()
        while True:
            if not self.queue.empty():
                start = time.time()
                result = self.queue.get()
                self.mic_todo = result['mic']
                self.laser_todo = result['laser']
                self.acc_x_todo = result['acc_x']
                self.acc_y_todo = result['acc_y']
                self.acc_z_todo = result['acc_z']
                # 0.002
                # print("R:", time.time()-start)

if __name__ == "__main__":
    queue_sensor = Queue()
    d = DataProcess(queue_sensor)
    f = FeatureProcess(queue_sensor)
    d.start()
    f.start()
