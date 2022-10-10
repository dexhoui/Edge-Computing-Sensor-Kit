#!/usr/bin/env python3.7.9
"""
Copyright © 2022 DUE TUL
@ desc  : This file is used to create the data list.
@ author: BOHAO CHU
@ email : bohao.chu@qq.com
"""
import os
import arguments as arg

"""
@ name     : get_mic_data_list
@ function : 
@ parameter: [mic_path, data path], [list_path, list path]
@ return   : None
"""
def get_mic_data_list(data_path, list_path):
    mic_data_path = os.path.join(data_path, 'mic')
    mic_list_path = os.path.join(list_path, 'mic_list.txt')
    mic_class_dir = os.listdir(mic_data_path)
    with open(mic_list_path, 'w') as f_mic:
        for i in range(len(mic_class_dir)):
            sound_dir = os.listdir(os.path.join(mic_data_path, mic_class_dir[i]))
            for sound_file in sound_dir:
                sound_file_path = os.path.join(mic_data_path, mic_class_dir[i], sound_file)
                f_mic.write('%s\t%d\n' % (sound_file_path, i))
            print("mic：%d/%d  %d" % (i + 1, len(mic_class_dir), len(sound_dir)))


"""
@ name     : _float_feature
@ function : 
@ parameter: This file is used to load raw data and exetract the feature for training.
@ return   : BOHAO CHU
"""
def get_acc_data_list(data_path, list_path):
    acc_data_path = os.path.join(data_path, 'acc')
    acc_list_path = os.path.join(list_path, 'acc_list.txt')
    acc_class_dir = os.listdir(acc_data_path)
    with open(acc_list_path, 'w') as f_acc:
        for i in range(len(acc_class_dir)):
            print(acc_data_path, acc_class_dir[i])
            acc_dir = os.listdir(os.path.join(acc_data_path, acc_class_dir[i]))
            for acc_file in acc_dir:
                acc_file_path = os.path.join(acc_data_path, acc_class_dir[i], acc_file)
                f_acc.write('%s\t%d\n' % (acc_file_path, i))
            print("acc：%d/%d  %d" % (i + 1, len(acc_class_dir), len(acc_dir)))


"""
@ name     : _float_feature
@ function : 
@ parameter: This file is used to load raw data and exetract the feature for training.
@ return   : BOHAO CHU
"""
def get_gyr_data_list(data_path, list_path):
    gyr_data_path = os.path.join(data_path, 'gyr')
    gyr_list_path = os.path.join(list_path, 'gyr_list.txt')
    gyr_class_dir = os.listdir(gyr_data_path)
    with open(gyr_list_path, 'w') as f_gyr:
        for i in range(len(gyr_class_dir)):
            gyr_dir = os.listdir(os.path.join(gyr_data_path, gyr_class_dir[i]))
            for gyr_file in gyr_dir:
                gyr_file_path = os.path.join(gyr_data_path, gyr_class_dir[i], gyr_file)
                f_gyr.write('%s\t%d\n' % (gyr_file_path, i))
            print("gyr：%d/%d  %d" % (i + 1, len(gyr_class_dir), len(gyr_dir)))


"""
@ name     : _float_feature
@ function : 
@ parameter: This file is used to load raw data and exetract the feature for training.
@ return   : BOHAO CHU
"""
def get_laser_data_list(data_path, list_path):
    laser_data_path = os.path.join(data_path, 'laser')
    laser_list_path = os.path.join(list_path, 'laser_list.txt')
    laser_class_dir = os.listdir(laser_data_path)
    with open(laser_list_path, 'w') as f_mpu:
        for i in range(len(laser_class_dir)):
            laser_dir = os.listdir(os.path.join(laser_data_path, laser_class_dir[i]))
            for laser_file in laser_dir:
                laser_file_path = os.path.join(laser_data_path, laser_class_dir[i], laser_file)
                f_mpu.write('%s\t%d\n' % (laser_file_path, i))
            print("laser  ：%d/%d  %d" % (i + 1, len(laser_class_dir), len(laser_dir)))


if __name__ == "__main__":
    print(os.getcwd())
    get_mic_data_list(arg.raw_data_path, arg.data_list_path)
    get_acc_data_list(arg.raw_data_path, arg.data_list_path)
    get_laser_data_list(arg.raw_data_path, arg.data_list_path)
