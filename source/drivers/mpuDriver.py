#!/usr/bin/env python3.8.9
'''
Copyright © 2021 DUE TUL
@ crea  : Thursday january 21, 2021
@ modi  : Tuesday February 02, 2022
@ desc  : This modules is used to read/write to MPU9250 sensor
@ author: Bohao Chu
'''
import smbus  # import SMBus module of I2C
import time  # import time function

'''
@ desc : some MPU9250 register and their address 
@ para : name of register of MPU
@ valu : address of register of MPU
'''
SLAVE_ADDRESS = 0x68  # MPU9250 Default I2C slave address
AK8963_SLAVE_ADDRESS = 0x0C  # AK8963 I2C slave address
DEVICE_ID = 0x71  # Device id

''' 
@ desc : MPU-9250 Register Addresses 
'''
SMPLRT_DIV = 0x19  # R25 Sample Rate Divider
CONFIG = 0x1A  # R26 Configure FIFO_MODE, EXT_SYNC_SET, DLPF_CFG
GYRO_CONFIG = 0x1B  # R27 Cyroscope Configuration, For full scale and FChoice_b
ACCEL_CONFIG = 0x1C  # R28 Accelerometer Configuration 1, For full scale
ACCEL_CONFIG_2 = 0x1D  # R29 Accelerometer Configuration 2, For FChoice_b and A_DLPFCFG
LP_ACCEL_ODR = 0x1E  # R30 Low Power Accelerometer ODR Control
WOM_THR = 0x1F  # R31 Wake-on Motion Threshold, LSB = 4mg. Range is 0mg to 1020mg
FIFO_EN = 0x23  # R35 FIFO Enable
I2C_MST_CTRL = 0x24  # R36 I2C Master Control
I2C_MST_STATUS = 0x36  # R54 I2C Master Control
INT_PIN_CFG = 0x37  # R55 INI Pin/Bypass Enable Configuration
INT_ENABLE = 0x38  # R56 Interrupt Enable
INT_STATUS = 0x3A  # R58 Interrupt Status
ACCEL_OUT = 0x3B  # R59 ACCEL_XOUT_H
TEMP_OUT = 0x41  # R65 TEMP_OUT_H
GYRO_OUT = 0x43  # R67 GYRO_OUT_H
WHO_AM_I = 0x75  # This register is used to verify the identity of the device

I2C_MST_DELAY_CTRL = 0x67
SIGNAL_PATH_RESET = 0x68
MOT_DETECT_CTRL = 0x69
USER_CTRL = 0x6A
PWR_MGMT_1 = 0x6B  # R107 Power Management 1
PWR_MGMT_2 = 0x6C  # R108 Power Management 2
FIFO_R_W = 0x74

''' 
@ desc : Gyro Full Scale Select 
'''
GFS_250 = 0x00  # R27 Gyro Full Scale Select 250dps
GFS_500 = 0x01  # R27 Gyro Full Scale Select 500dps
GFS_1000 = 0x02  # R27 Gyro Full Scale Select 1000dps
GFS_2000 = 0x03  # R27 Gyro Full Scale Select 2000dps

''' 
@ desc : Accel Full Scale Select 
'''
AFS_2G = 0x00  # R28 Accel Full Scale Select 2G
AFS_4G = 0x01  # R28 Accel Full Scale Select 4G
AFS_8G = 0x02  # R28 Accel Full Scale Select 8G
AFS_16G = 0x03  # R28 Accel Full Scale Select 16G

''' 
@ desc : AK8963 Register Addresses 
'''
AK8963_ST1 = 0x02
AK8963_MAGNET_OUT = 0x03
AK8963_CNTL1 = 0x0A
AK8963_CNTL2 = 0x0B
AK8963_ASAX = 0x10

# CNTL1 Mode select

AK8963_MODE_DOWN = 0x00  # Power down mode
AK8963_MODE_ONE = 0x01  # One shot data output

AK8963_MODE_C8HZ = 0x02  # Continous data output 8Hz
AK8963_MODE_C100HZ = 0x06  # Continous data output 100Hz

# Magneto Scale Select
AK8963_BIT_14 = 0x00  # 14bit output
AK8963_BIT_16 = 0x01  # 16bit output

# smbus
bus = smbus.SMBus(1)


class MPU9250:
    '''
    @desc Constructor
    @param [1] self The object pointer
    @param [2] address MPU-9250 I2C slave address default:0x68
    '''

    def __init__(self, address=SLAVE_ADDRESS):
        self.address = address
        self.configMPU9250(GFS_250, AFS_2G)
        time.sleep(1)
        self.configAK8963(AK8963_MODE_C100HZ, AK8963_BIT_16)
        if (self.searchDevice()):
            print("# mpu is initializing")
        else:
            print("mpu is in error\n")

    '''
    @desc Search Device
    @param [in] self The object pointer.
    @retval true device connected
    @retval false device error
    '''

    def searchDevice(self):
        who_am_i = bus.read_byte_data(self.address, WHO_AM_I)
        if (who_am_i == DEVICE_ID):
            return True
        else:
            return False

    '''
    @desc Configure MPU-9250
    @param [1] self The object pointer.
    @param [2] gfs Gyro Full Scale Select(default:GFS_250[+250dps])
    @param [3] afs Accel Full Scale Select(default:AFS_2G[2g])
    '''

    def configMPU9250(self, gfs, afs):
        if gfs == GFS_250:
            self.gres = 250.0 / 32768.0
        elif gfs == GFS_500:
            self.gres = 500.0 / 32768.0
        elif gfs == GFS_1000:
            self.gres = 1000.0 / 32768.0
        else:  # gfs == GFS_2000
            self.gres = 2000.0 / 32768.0

        if afs == AFS_2G:
            self.ares = 2.0 / 32768.0
        elif afs == AFS_4G:
            self.ares = 4.0 / 32768.0
        elif afs == AFS_8G:
            self.ares = 8.0 / 32768.0
        else:  # afs == AFS_16G:
            self.ares = 16.0 / 32768.0

        # sleep off
        bus.write_byte_data(self.address, PWR_MGMT_1, 0x00)
        time.sleep(0.1)
        # auto select clock source
        bus.write_byte_data(self.address, PWR_MGMT_1, 0x01)
        time.sleep(0.1)
        # sample rate divider - [7:0]SMPLRT_DIV
        bus.write_byte_data(self.address, SMPLRT_DIV, 0x00)
        time.sleep(0.1)
        # DLPF_CFG - [6]FIFO_MODE [5:3]EXT_SYNC_SET [2:0]DLPF_CFG
        bus.write_byte_data(self.address, CONFIG, 0x07)
        time.sleep(0.1)
        # open acc and gyro
        bus.write_byte_data(self.address, PWR_MGMT_2, 0x00)
        time.sleep(0.1)
        # gyro full scale select
        bus.write_byte_data(self.address, GYRO_CONFIG, gfs << 3)
        time.sleep(0.1)
        # accel full scale select
        bus.write_byte_data(self.address, ACCEL_CONFIG, afs << 3)
        time.sleep(0.1)
        # A_DLPFCFG - [3]accel_fchoice_b [2:0]A_DLPFCFG
        bus.write_byte_data(self.address, ACCEL_CONFIG_2, 0x00)
        time.sleep(0.1)
        # BYPASS_EN
        bus.write_byte_data(self.address, INT_PIN_CFG, 0x02)
        time.sleep(0.1)

    '''
    @desc Configure AK8963
    @param [1] self The object pointer.
    @param [2] mode Magneto Mode Select(default:AK8963_MODE_C8HZ[Continous 8Hz])
    @param [3] mfs Magneto Scale Select(default:AK8963_BIT_16[16bit])
    '''

    def configAK8963(self, mode, mfs):
        if mfs == AK8963_BIT_14:
            self.mres = 4912.0 / 8190.0
        else:  # mfs == AK8963_BIT_16:
            self.mres = 4912.0 / 32760.0

        bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, 0x00)
        time.sleep(0.01)
        # set read FuseROM mode
        bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, 0x0F)
        time.sleep(0.01)
        # read coef data
        data = bus.read_i2c_block_data(AK8963_SLAVE_ADDRESS, AK8963_ASAX, 3)

        self.magXcoef = (data[0] - 128) / 256.0 + 1.0
        self.magYcoef = (data[1] - 128) / 256.0 + 1.0
        self.magZcoef = (data[2] - 128) / 256.0 + 1.0

        # set power down mode
        bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, 0x00)
        time.sleep(0.01)
        # set scale&continous mode
        bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, (mfs << 4 | mode))
        time.sleep(0.01)
        print("MPU9250 : Magnetometer configuration complete. ")

    '''
    @desc brief Check data ready
    @param [1] self The object pointer.
    @retval true data is ready
    @retval false data is not ready
    '''

    def checkDataReady(self):
        drdy = bus.read_byte_data(self.address, INT_STATUS)
        if drdy & 0x01:
            return True
        else:
            return False

    '''
    @desc Read accelerometer
    @param [1] self The object pointer.
    @retval x : x-axis data
    @retval y : y-axis data
    @retval z : z-axis data
    '''

    def readAccel(self):
        data = bus.read_i2c_block_data(self.address, ACCEL_OUT, 6)
        x = self.dataConv(data[1], data[0])
        y = self.dataConv(data[3], data[2])
        z = self.dataConv(data[5], data[4])

        x = round(x * self.ares, 3)
        y = round(y * self.ares, 3)
        z = round(z * self.ares, 3)
        # 0.00029s = 3333 = 4K*16bit*3 = 192Kbit/s  - 400Kbit/s(I2C)
        # 0.00094s = 3333 = 1K*16bit*3 = 48Kbit/s   - 100Kbit/s(I2C)
        return {"x": x, "y": y, "z": z}

    def acc_sample(self):
        data_x = []
        data_y = []
        data_z = []
        for i in range(0, 500):
            accel = self.readAccel()
            data_x.append(accel['x'])
            data_y.append(accel['y'])
            data_z.append(accel['z'])
        return {"x": data_x, "y": data_y, "z": data_z}

    '''
    @desc Read gyro
    @param [in] self The object pointer.
    @retval x : x-gyro data
    @retval y : y-gyro data
    @retval z : z-gyro data
    '''

    def readGyro(self):
        data = bus.read_i2c_block_data(self.address, GYRO_OUT, 6)
        x = self.dataConv(data[1], data[0])
        y = self.dataConv(data[3], data[2])
        z = self.dataConv(data[5], data[4])

        x = round(x * self.gres, 3)
        y = round(y * self.gres, 3)
        z = round(z * self.gres, 3)

        # 0.00029s = 3333 = 4K*16bit = 64Kbit/s   - 400Kbit/s(I2C)
        # 0.00093s = 3333 = 1K*16bit = 16Kbit/s   - 100Kbit/s(I2C)
        return {"x": x, "y": y, "z": z}


    def gyr_sample(self):
        data_x = []
        data_y = []
        data_z = []
        for i in range(0, 500):
            gyr = self.readGyro()
            data_x.append(gyr['x'])
            data_y.append(gyr['y'])
            data_z.append(gyr['z'])
        return {"x": data_x, "y": data_y, "z": data_z}


    '''
    @desc Read magneto
    @param [in] self The object pointer.
    @retval x : X-magneto data
    @retval y : y-magneto data
    @retval z : Z-magneto data
    '''

    def readMagnet(self):
        x = 0
        y = 0
        z = 0
        # check data ready
        drdy = bus.read_byte_data(AK8963_SLAVE_ADDRESS, AK8963_ST1)
        if drdy & 0x01:
            data = bus.read_i2c_block_data(AK8963_SLAVE_ADDRESS, AK8963_MAGNET_OUT, 7)

            # check overflow
            if (data[6] & 0x08) != 0x08:
                x = self.dataConv(data[0], data[1])
                y = self.dataConv(data[2], data[3])
                z = self.dataConv(data[4], data[5])

                x = round(x * self.mres * self.magXcoef, 3)
                y = round(y * self.mres * self.magYcoef, 3)
                z = round(z * self.mres * self.magZcoef, 3)

        # max rate = 100Hz
        # 0.0004s  - 400Kbit/s(I2C)
        # 0.00146s = 1000 = 1K*14bit = 14Kbit/s   - 100Kbit/s(I2C)
        return {"x": x, "y": y, "z": z}

    def mag_sample(self):
        accel = self.readMagnet()
        return accel['z']

    '''
    @desc Read temperature
    @param [out] temperature temperature(degrees C)
    '''

    def readTemperature(self):
        data = bus.read_i2c_block_data(self.address, TEMP_OUT, 2)
        temp = self.dataConv(data[1], data[0])

        temp = round((temp / 333.87 + 21.0), 3)
        return temp

    '''
    @desc Data Convert
    @param [in] self The object pointer.
    @param [in] data1 LSB
    @param [in] data2 MSB
    @retval Value MSB+LSB(int 16bit)
    '''

    def dataConv(self, data1, data2):
        value = data1 | (data2 << 8)
        if (value & (1 << 16 - 1)):
            value -= (1 << 16)
        return value


if __name__ == "__main__":
    mpu = MPU9250()
    while True:
        print(mpu.readAccel(), mpu.readGyro(), mpu.readMagnet())
        time.sleep(0.5)
