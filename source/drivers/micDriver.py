#!/usr/bin/env python3.7.3
"""
Copyright © 2021 DUE TUL
@ crea  : Sunday February 14, 2021
@ modi  : Sunday February 14, 2021
@ desc  : This modules is used for audio
@ author: Bohao Chu
"""
import time, wave, datetime, os, sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import pyaudio
import numpy as np
import arguments as arg



CHUNK = 750
SAMPRATE = 15000
PYADUIOFORMAT = pyaudio.paInt16
buffer_format = np.int16
CHANNELS = 1
record_length = 1


def device_check():
    audio = pyaudio.PyAudio()
    # print audio card
    for ii in range(0, audio.get_device_count()):
        print(audio.get_device_info_by_index(ii))


def audio_start():
    print("INMP441: MIC STAR\n")
    audio = pyaudio.PyAudio()
    stream = audio.open(format=PYADUIOFORMAT,
                        rate=SAMPRATE,
                        channels=CHANNELS,
                        input=True,
                        frames_per_buffer=CHUNK)
    stream.stop_stream()
    stream.start_stream()
    while stream.is_active():
        start = time.time()
        stream_data = stream.read(CHUNK, exception_on_overflow=False)
        end = time.time()
        print(end - start)
        print(np.frombuffer(stream_data, dtype=buffer_format).shape)
    stream.stop_stream()


def audio_end(stream, audio):
    stream.close()
    audio.terminate()
    print("INMP441: MIC End\n")

'''
def data_grabber(stream, record_len):
    stream.start_stream()
    data, data_frames = [], []
    for frame in range(int((SAMPRATE * record_len) / CHUNK)):
        stream_data = stream.read(CHUNK, exception_on_overflow=False)
        data_frames.append(stream_data)
        data.append(np.frombuffer(stream_data, dtype=buffer_format))
    stream.stop_stream()
    return data, data_frames
'''


def data_saver(audio, data_folder, data_frames, start_time, name):
    if os.path.isdir(data_folder) == False:
        os.mkdir(data_folder)
    filename = datetime.datetime.strftime(start_time, '%Y%m%d-%H%M%S-%f-')
    wf = wave.open(data_folder + filename + name+ '.wav', 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(PYADUIOFORMAT))
    wf.setframerate(SAMPRATE)
    wf.writeframes(b''.join(data_frames))
    wf.close()
    return filename

def mic_test():
    audio = pyaudio.PyAudio()
    chunk = arg.chunk
    stream = audio.open(format=pyaudio.paInt16, rate=15000, channels=1, input=True, frames_per_buffer=chunk)
    stream.start_stream()
    time.sleep(1)
    stream_data = stream.read(chunk, exception_on_overflow=False)
    audio_data = np.frombuffer(stream_data, dtype=np.int16)
    print(audio_data.shape)
    stream.stop_stream()

def INMP441():
    print("# microphone is initializing")
    audio = pyaudio.PyAudio()
    # print(audio.get_default_input_device_info())
    chunk = arg.chunk
    time.sleep(0.1)
    stream = audio.open(format=pyaudio.paInt16, rate=15000, channels=1, input=True, frames_per_buffer=chunk)
    time.sleep(0.1)
    stream.stop_stream()
    time.sleep(0.5)
    stream.start_stream()
    return stream, audio


if __name__ == "__main__":
    mic_test()
