
# **Hardware**
**Editor:** Bohao Chu, **Date:** 23.09.2022, **Email:** bohao.chu@qq.com

**Supervisor:**  Fuyin Wei, Fei Xiang, Bernd Noche

The **Edge Computing Sensor Kit Hardware** is consist of two parts, **Compute Module 4** and **Sensor Kit**. The Compute Module 4 can be bought in stores, and the Sensor Kit can be got via PCB Producer by providing our PCB file.

We designed our Sensor Kit via Altium Designer 22,  Without going into too much detail about the design of the PCB, I have made the  [source project](/hardware/printed%20circuit%20board/) available.


![CM4 IO Board](/assets/images/hardware/ecsk1.jpg "CM4 IO Board")


## **Compute Module 4**
In this chapter, I will discribe how to use it. 
[More information about Compute Module 4](https://www.raspberrypi.com/products/compute-module-4/?variant=raspberry-pi-cm4001000)

### **A. Flashing new OS ot Compute Module 4 eMMC**
We have to use an io board for flashing operation system. The requirementes for flashing the Compute Module 4 eMMC as follows:

- [Compute Module 4](https://www.raspberrypi.com/products/compute-module-4/?variant=raspberry-pi-cm4001000)
- [IO Board](https://www.waveshare.com/wiki/CM4-IO-BASE-A) ( other io boards are also available. )
- [Windows Installer](https://github.com/raspberrypi/usbboot/raw/master/win32/rpiboot_setup.exe) ( download it and insatll it, it may need to wait a while.)
- [Raspberry Pi Imager](https://downloads.raspberrypi.org/imager/imager_latest.exe)( download it and insatll it. )

#### **A1. Install Compute Module 4 on IO Board**
We used [Waveshare CM4 IO Board](https://www.waveshare.com/wiki/CM4-IO-BASE-A) as our IO board.
Ensure the Compute Module is fitted correctly installed on the IO board. It should lie flat on the IO board.

![CM4 IO Board](/assets/images/hardware/CM4-IO-BASE-A-details-3.jpg "CM4 IO Board")

#### **A2. Setup IO Board to USB model**
After the CM4 was installed on the IO Board, we should set IO Board to USB model by setting the switch to **ON**. Then plug your host PC USB into the USB SLAVE port. Supply power to the board.

![CM4 IO Board](/assets/images/hardware/usb-model.jpg "CM4 IO Board")

#### **A3. Open rpiboot on windows**
This software is used to install the drivers and boot tool. After a few seconds, the Compute Module eMMC will pop up under Windows as a disk (USB mass storage device).

![CM4 IO Board](/assets/images/hardware/rpiboot.png "CM4 IO Board")

It may need to **wait a while**. *If you get stuck here, unplug the USB and then plug it into the PC again.*

![CM4 IO Board](/assets/images/hardware/rpiboots.png "CM4 IO Board")

Then the CM4 will pop under windows as a **disk**.

![CM4 IO Board](/assets/images/hardware/rpiboot3.png "CM4 IO Board")

#### **A4. Open RPI Imager on windows**
First, click the **CHOOSE OS** button, then select the **Raspberry Pi OS(other)** button, then choose the **Raspberry Pi OS(64-bit)** or **Raspberry Pi OS Lite(64-bit)**. Here I choosed the **Raspberry Pi OS(64-bit)** without Deskpot.

![CM4 IO Board](/assets/images/hardware/imager1.png "CM4 IO Board")

Second, click the **CHOOSE STORAGE**  button, then choose **RPI-MSD-0001** item.

![CM4 IO Board](/assets/images/hardware/imager2.png "CM4 IO Board")

Third, click the **Setting**  button.
1. Select **Set hostname** and input "sensor".
2. Select **Enable SSH** and **use password authentication**.
3. Select **Set username and password**. set username to "pi", password to "123456". 
4. **Configure wireless LAN**, input name and password of WiFi. Set wireless LAN country as DE(Germany).
5. Select **Set locale settings**, set Time zone to "Europe/Berlin", Keyboard layout to "us".
6. Select **Eject media when finished** and **Enable telemetry**.

![CM4 IO Board](/assets/images/hardware/imager4.png "CM4 IO Board")

Finally, Click the **WRITE** button and choose **YES**, then wait a while.

![CM4 IO Board](/assets/images/hardware/imager3.png "CM4 IO Board")


## **Sensor Kit**
After the OS was flashed into CM4, then uninstall CM4 from the io board, and install it on our edge computing sensor kit. Then supply 5V/3A (Not less than 2A) power to our Sensor Kit.

### **A. Config the WiFi**
We did not add the ethernet port to our sensor kit due to the space limitation and the Internet is not necesarry, but you can use the WiFi of CM4 to connect the Internet. You can use this way to change the WiFi SSID and WiFi Password so that the ECSK can be applied on anywhere with wifi.

1. Install the CM4 on IO board.

2. Setup IO Board to USB model and connect the USB to the PC, and then supply power to the IO Board.

3. Open rpiboot on windows, the CM4 will pop up under Windows as a disk. 

4. Enter this disk and make a new file named "wpa_supplicant.conf", and edit it with the following content.
>
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1
    network={
        ssid="WiFi SSID"
        psk="WiFi Password"
    }
>

5. Then install CM4 on oure Sensor Kit and start up. After a while, it will automatically connect to the WiFi you have configured.