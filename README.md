# diyclock 
Raspberry Pi Python project

This is one of my Do It Yourself Home Automation System (DIYHAS) projects. It requires a Raspberry Pi Zero W with interfaces to two I2C devices, a PIR motion sensor and a MOSFET to control a 12 volt piezo buzzer. The I2C devices are from Adafruit and uses their backback interface. I really like the 8x8 LED matrix and had fun building classes for different designs.

- You will need two Adafruit python libraries 
```
git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
cd Adafruit_Python_GPIO
sudo python3 setup.py install
cd ..
git clone https://github.com/adafruit/Adafruit_Python_LED_Backpack.git 
cd Adafruit_Python_LED_Backpack
sudo python3 setup.py install
cd ..
```
An Adafruit protoboard diagram is also included in the repository.
