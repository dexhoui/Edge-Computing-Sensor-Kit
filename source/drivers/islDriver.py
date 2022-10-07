import smbus
import time

# Get I2C bus
bus = smbus.SMBus(3)

# ISL29125 address, 0x44(68)
# Select configuation-1register, 0x01(01)
#               0x0D(13)        Operation: RGB, Range: 10000 lux, Res: 16 Bits
bus.write_byte_data(0x44, 0x01, 0x0D)

if __name__=="__main__":
    while True:
        data = bus.read_i2c_block_data(0x44, 0x09, 6)
        time.sleep(0.5)
        # Convert the data
        green = data[1] * 256 + data[0]
        red = data[3] * 256 + data[2]
        blue = data[5] * 256 + data[4]
        # Output data to the screen
        print("Green Color luminance : %d lux" %green)
        print("Red Color luminance : %d lux" %red)
        print("Blue Color luminance : %d lux" %blue)