#!/usr/bin/python3.7.3
"""
Copyright © 2021 DUE TUL
@ crea  : Thursday january 21, 2021
@ modi  : Tuesday february 02, 2021
@ desc  : This modules is used to sample
@ author: Bohao Chu
"""
import sys
import time
import mpuDriver
import datetime
from tqdm import tqdm

mpu9250 = mpuDriver.MPU9250()  # Create a new mpu9250 object
mpu9250.searchDevice()  # Verify whether the connection is successful

'''
When an action occurs, please use the corresponding path as the parameter of the sample function.
'''

def acc_sample(path, amount):
    if amount % 1000 != 0:
        print("Please enter a multiple of 1000")
        sys.exit(0)
    print("The raw data of acc will be saved in " + path)
    print("The acc sampling program starts after 3 seconds")
    time.sleep(1)
    with open(path, 'a') as f_mpu:
        for i in tqdm(range(amount)):
            start = time.time()
            accel = mpu9250.readAccel()
            f_mpu.write("{}, {}, {}, {}\r\n".format(start, accel['x'], accel['y'], accel['z']))


if __name__=="__main__":
    try:
        for i in range(8):
            filename = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            acc_sample("../database/with-noise/mpu/open-right/"+filename+ "-Open-Right", 100*1000)
    except KeyboardInterrupt as E:
        print("User terminated the program")
    finally:
        print("The sampling programm is over")
