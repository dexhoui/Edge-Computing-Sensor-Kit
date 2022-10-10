import os, sys, time
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.dirname(SCRIPT_DIR)
ROOT_DIR = os.path.dirname(SOURCE_DIR)
sys.path.append(SOURCE_DIR)
sys.path.append(ROOT_DIR)
print("# function     : sampling")
print("# current path :", SCRIPT_DIR)
print("# source  path :", SOURCE_DIR)
print("# root    path :", ROOT_DIR)
print("# note         : please change the scene name and activity in file arguments\n")
time.sleep(5)

import drivers.mpuDriver as mpuD
import drivers.micDriver as micD
import drivers.laserDriver as laserD
import drivers.bmeDriver as bmeD
import time, statistics
import threading
import numpy as np
import multiprocessing as mp
import tflite_runtime.interpreter as tflite
import datav.datav as dv
import feature.feature as fea
import arguments as arg
import smbus, wave, datetime
import pyaudio
import qwiic

import busio
import board
import adafruit_amg88xx

# default duration is 50s.
_duration = arg.duration

# tensorflow default float32, numpy default float64
'''
@ name      : DataProcess
@ desc      : Accel Full Scale Select
@ parameter : 
@ return    :
'''
class DataProcess(mp.Process):
    def __init__(self, queue_mic, queue_acc):
        super(DataProcess, self).__init__()
        self.mpu = mpuD.MPU9250()
        self.mic, self.audio = micD.INMP441()
        self.laser = laserD.VL53L1()
        self.eye = adafruit_amg88xx.AMG88XX(busio.I2C(board.SCL, board.SDA))
        self.color = smbus.SMBus(3)
        self.queue_mic = queue_mic
        self.queue_acc = queue_acc

        # raw data placeholder
        self.mic_todo = [1 for i in range(7500)]
        self.acc_x_todo = [1 for i in range(500)]
        self.acc_y_todo = [1 for i in range(500)]
        self.acc_z_todo = [1 for i in range(500)]
        self.eye_todo = [1 for i in range(64)]
        self.laser_todo = [1 for i in range(2)]
        self.color_todo = [1 for i in range(3)]
        self.bme_todo = [1 for i in range(3)]
        self.mag_todo = [1 for i in range(3)]

    '''
        @ name      : mic_raw
        @ desc      : sample from sensor microphone INMP441 and save raw for training
        @ parameter : self
        @ return    : none
    '''
    def mic_raw(self):
        print(f"microphone is sampling for {arg.activity}",  time.time())
        index = burning_time = 0
        audio_frames = []
        while self.mic.is_active():
            start = time.time()
            stream_data = self.mic.read(arg.chunk, exception_on_overflow=False)
            audio_frames.append(stream_data)
            burning_time = burning_time + time.time() - start
            index = index + 1
            if index == _duration*2:
                print('microphone stop sampling and the real sample rate is ', 7500/(burning_time / (_duration * 2)))
                file_dir = f'{ROOT_DIR}/dataset/{arg.dataset}/mic/{arg.activity}/'
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir)
                filename = f'{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")}-{arg.activity}.wav'
                wf = wave.open(file_dir + filename, 'wb')
                wf.setnchannels(1)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(15000)
                wf.writeframes(b''.join(audio_frames))
                wf.close()
                self.mic.stop_stream()
                return

    '''
        @ name      : mpu_acc_raw
        @ desc      : sample from acc sensor MPU9250 and save raw for training
        @ parameter : self
        @ return    : none
    '''
    def mpu_acc_raw(self):
        print(f"# mpu acc is sampling for {arg.activity}",  time.time())
        index = burning_time = 0
        # check if the direction exists, and create this direction if it does not.
        file_dir = f'{ROOT_DIR}/dataset/{arg.dataset}/acc/{arg.activity}/'
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        # create the filename using current date and time.
        filename = f'{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")}-{arg.activity}.txt'
        with open(file_dir + filename, 'a') as f_acc:
            while True:
                start = time.time()
                acc = self.mpu.readAccel()
                time.sleep(0.0006)
                f_acc.write("{}, {}, {}, {}\r\n".format(index, acc['x'], acc['y'], acc['z']))
                burning_time = burning_time + time.time() - start
                index = index + 1
                if index % (1000 * _duration) == 0:
                    print('mpu acc stop sampling and the real sample rate is', 1 / (burning_time / (1000 * _duration)))
                    return


    def mpu_mag_raw(self):
        time.sleep(2)
        print(f"# mpu mag is sampling")
        last_mag = 0
        while True:
            mag = []
            for i in range(10):
                mag.append(self.mpu.readMagnet()['x'])
                time.sleep(0.04)
            mag = statistics.mean(mag)
            if mag - last_mag > 2:
                self.mag_todo = mag
                # print('up', mag-last_mag)
            elif mag - last_mag < -2:
                self.mag_todo = mag
                # print('down', mag-last_mag)
            else:
                self.mag_todo = mag
                # print('noupnodown', mag-last_mag)
            last_mag = mag


    '''
        @ name      : laser
        @ desc      : sample from distance sensor VL53L1X and save raw for training
        @ parameter : self
        @ return    : none
    '''
    def laser_raw(self):
        last_distance = 0
        print(f"# laser is sampling")
        while self.laser.check_for_data_ready():
            distance = []
            for i in range(10):
                distance.append(self.laser.get_distance()/10)
                time.sleep(0.04)
            distance = statistics.mean(distance)
            if last_distance - distance > 0.2:
                self.laser_todo[0] = 0
            elif last_distance - distance < -0.2:
                self.laser_todo[0] = 2
            else:
                self.laser_todo[0] = 1
            last_distance = distance
            self.laser_todo[1] = distance
        self.laser.stop_ranging()


    def eye_raw(self):
        time.sleep(2)
        print(f"# eye is sampling")
        while True:
            eye = []
            for row in self.eye.pixels:
                for i in range(8):
                    eye.append(row[7-i]+20)
            self.eye_todo = eye
            time.sleep(0.5)

    def color_raw(self):
        self.color.write_byte_data(0x44, 0x01, 0x0D)
        time.sleep(2)
        print(f"# color is sampling")
        while True:
            data = self.color.read_i2c_block_data(0x44, 0x09, 6)
            time.sleep(0.5)
            # Convert the data
            self.color_todo[0] = data[3] * 256 + data[2]
            self.color_todo[1] = data[1] * 256 + data[0]
            self.color_todo[2] = data[5] * 256 + data[4]

    def bme_raw(self):
        time.sleep(2)
        print(f"# bme is sampling")
        while True:
            temperature, pressure, humidity = bmeD.readBME280All()
            time.sleep(0.5)
            self.bme_todo[0] = temperature
            self.bme_todo[1] = humidity
            self.bme_todo[2] = pressure/100

    def run(self):
        try:
            print("# data process id : ", os.getpid())
            threads = []
            t1 = threading.Thread(target=self.mic_raw)
            threads.append(t1)
            t2 = threading.Thread(target=self.mpu_acc_raw)
            threads.append(t2)
            t3 = threading.Thread(target=self.eye_raw)
            threads.append(t3)
            t4 = threading.Thread(target=self.laser_raw)
            threads.append(t4)
            t5 = threading.Thread(target=self.color_raw)
            threads.append(t5)
            t6 = threading.Thread(target=self.bme_raw)
            threads.append(t6)
            t7 = threading.Thread(target=self.mpu_mag_raw)
            threads.append(t7)
            for t in threads:
                t.start()
            while True:
                if not self.queue_mic.full():
                    data = {'mic': self.mic_todo}
                    self.queue_mic.put(data)
                if not self.queue_acc.full():
                    data = {'acc_x': self.acc_x_todo,
                            'acc_y': self.acc_y_todo,
                            'acc_z': self.acc_z_todo,
                            'laser': self.laser_todo,
                            'eye'  : self.eye_todo,
                            'color': self.color_todo,
                            'bme': self.bme_todo
                            }
                    self.queue_acc.put(data)
                time.sleep(0.5)
        except KeyboardInterrupt:
            print('# DATAP: Is KeyboardInterrupt')
            self.mic.stop_stream()
            self.mic.close()
            self.audio.terminate()
            self.laser.stop_ranging()
            sys.exit()



class MicFeatureProcess(mp.Process):
    def __init__(self, queue_in, queue_out):
        super(MicFeatureProcess, self).__init__()
        self.queue_in = queue_in
        self.queue_out = queue_out

    def run(self):
        print("# mic feature process id : ", os.getpid())
        i = 0
        tmp = []
        tmp_feature = np.random.random((60, 1))
        while True:
            if not self.queue_in.empty():
                result = self.queue_in.get()
                mic_feature = fea.micfeature(result['mic'])
                if i < 100:
                    i = i + 1
                    tmp.extend(result['mic'])
                    tmp_feature = np.concatenate((tmp_feature, mic_feature), axis=1)
                else:
                    i = 0
                    dv.datasave('mic', tmp)
                    fea.featuresave('mic', np.array(tmp_feature))
                    tmp = []
                    tmp_feature = mic_feature

                self.queue_out.put(mic_feature)


class AccFeatureProcess(mp.Process):
    def __init__(self, queue_in, queue_out):
        super(AccFeatureProcess, self).__init__()
        self.queue_in = queue_in
        self.queue_out = queue_out

    def run(self):
        print("# acc feature process id : ", os.getpid())
        i = 0
        tmp = []
        tmp_feature = np.random.random((60, 1))
        while True:
            if not self.queue_in.empty():
                result = self.queue_in.get()
                acc_x_feature, acc_y_feature, acc_z_feature = fea.accfreature(result['acc_x'], result['acc_y'], result['acc_z'])
                if i < 100:
                    i = i + 1
                    tmp.extend(result['acc_x'])
                    tmp_feature = np.concatenate((tmp_feature, acc_x_feature), axis=1)
                else:
                    i = 0
                    dv.datasave('acc_x', tmp)
                    fea.featuresave('acc_x', tmp_feature)
                    tmp_feature = acc_x_feature
                    tmp = []
                laser_feature = result['laser']
                data = {'acc_x': acc_x_feature,
                        'acc_y': acc_y_feature,
                        'acc_z': acc_z_feature,
                        'laser': laser_feature,
                        'eye'  : result['eye'],
                        'color': result['color'],
                        'bme': result['bme'],
                        }
                self.queue_out.put(data)


class RecoModelProcess(mp.Process):
    def __init__(self, queue_mic_fea, queue_acc_fea):
        super(RecoModelProcess, self).__init__()
        self.queue_mic_fea = queue_mic_fea
        self.queue_acc_fea = queue_acc_fea


        # feature placeholder
        self.mic_feature = np.random.random((60, 66))
        self.acc_x_feature = np.random.random((60, 8))
        self.acc_y_feature = np.random.random((60, 8))
        self.acc_z_feature = np.random.random((60, 8))
        self.laser_feature = np.random.random((60, 1))

    '''
         @ name      : mpu_gyr_raw
         @ desc      : sample from gyr sensor MPU9250 and save raw for training
         @ parameter : self
         @ return    : none
     '''


    def run(self):
        print("# model process id : ", os.getpid())
        spin_interpreter = tflite.Interpreter(model_path=f"{ROOT_DIR}/models/inference/on.tflite")
        spin_interpreter.allocate_tensors()
        up_interpreter = tflite.Interpreter(model_path=f"{ROOT_DIR}/models/inference/on.tflite")
        up_interpreter.allocate_tensors()
        down_interpreter = tflite.Interpreter(model_path=f"{ROOT_DIR}/models/inference/on.tflite")
        down_interpreter.allocate_tensors()
        #print(spin_interpreter.get_output_details())

        input_details = spin_interpreter.get_input_details()
        #print(spin_interpreter.get_input_details())
        input_index = input_details[0]['index']
        # 0-fin: 96, 1-mic: 58, 2-x:68, 3-y:78, 4-z:88, 5-laser:93

        while True:
            pred_resutl = []
            if not self.queue_mic_fea.empty():
                result = self.queue_mic_fea.get()
                self.mic_feature = result
            if not self.queue_acc_fea.empty():
                result = self.queue_acc_fea.get()
                self.acc_x_feature = result['acc_x']
                self.acc_y_feature = result['acc_y']
                self.acc_z_feature = result['acc_z']
                self.laser_feature = [result['laser'][0] for i in range(60)]
                laser_data = result['laser'][1]
                eye_data = result['eye']
                color_data = result['color']
                bme_data = result['bme']
                merge_feature = np.column_stack((self.mic_feature,
                                                 self.acc_x_feature,
                                                 self.acc_y_feature,
                                                 self.acc_z_feature,
                                                 self.laser_feature)).astype(dtype=np.float32).reshape(1, 60, 91, 1)

                spin_interpreter.set_tensor(input_index, merge_feature)
                spin_interpreter.invoke()
                spin_output = spin_interpreter.get_tensor(58)

                up_interpreter.set_tensor(input_index, merge_feature)
                up_interpreter.invoke()
                up_output = up_interpreter.get_tensor(68)

                down_interpreter.set_tensor(input_index, merge_feature)
                down_interpreter.invoke()
                down_output = down_interpreter.get_tensor(93)
                downa_output = down_interpreter.get_tensor(96)
                # print(downa_output, spin_output, up_output, down_output)
                if spin_output > 0.2:
                    pred_resutl.append('spin')
                    # print(f"spin       : Y")
                if result['laser'][0] == 2:
                    pred_resutl.append('upward')
                    # print(f"upward     : Y")

                if result['laser'][0] == 0:
                    pred_resutl.append('downward')
                    # print(f"downward   : Y")

                # 0.18s
                # dv.featurev(self.mic_feature, self.acc_x_feature, self.acc_y_feature, self.acc_z_feature,self.laser_feature[0], pred_resutl, laser_data, eye_data, color_data, bme_data)

if __name__ == "__main__":
    try:
        print("main process id:", os.getpid())
        queue_mic_raw = mp.Queue()
        queue_acc_raw = mp.Queue()
        queue_mic_fea = mp.Queue()
        queue_acc_fea = mp.Queue()
        d = DataProcess(queue_mic_raw, queue_acc_raw)
        m = MicFeatureProcess(queue_mic_raw, queue_mic_fea)
        a = AccFeatureProcess(queue_acc_raw, queue_acc_fea)
        r = RecoModelProcess(queue_mic_fea, queue_acc_fea)
        d.start()
        m.start()
        a.start()
        r.start()
    finally:
        time.sleep(3)
        print("\n# please type ctrl+c to stop program")

