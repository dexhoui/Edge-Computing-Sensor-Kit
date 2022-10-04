import qwiic
import time


def VL53L1():
    tof = qwiic.QwiicVL53L1X()
    tof.stop_ranging()
    time.sleep(0.5)
    if not tof.sensor_init():
        print("# laser is initializing")
    else:
        print("VL53L1X: Laser online!")

    tof.set_distance_mode(1)
    tof.set_timing_budget_in_ms(100)
    tof.start_ranging()
    time.sleep(0.5)
    return tof

class VL53L1X():
    def __init__(self):
        # address = 0x29
        self.ToF = qwiic.QwiicVL53L1X()
        if (self.ToF.sensor_init() == None):  # Begin returns 0 on a good init
            print("VL53L1X: Laser online!\n")
        else:
            print("VL53L1X: Laser offline!\n")
        self.ToF.set_distance_mode(1)  # Sets Distance Mode Short (Long- Change value to 2)

    def test(self):
        self.ToF.start_ranging()  # Write configuration bytes to initiate measurement
        time.sleep(0.5)
        print(self.ToF.get_distance())
        self.ToF.stop_ranging()

    def sample(self):
        self.ToF.start_ranging()  # Write configuration bytes to initiate measurement
        time.sleep(1)
        while self.ToF.check_for_data_ready():
            start = time.time()
            time.sleep(0.05)
            print(self.ToF.get_distance())
            end = time.time()
            print(end-start)
        # max rate = 50Hz
        # 0.00054s = 2000Hz - 400Kbit/s(I2C)
        # 0.0015s  = 800Hz  - 100Kbit/s(I2C)


if __name__=="__main__":
    laser = VL53L1X()
    laser.test()