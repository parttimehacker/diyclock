#!/usr/bin/python3
""" Example of the Wargames' WOPR 8x8 LED matrix dispplay class """

from threading import Lock

from Adafruit_GPIO import GPIO
from Adafruit_LED_Backpack import BicolorMatrix8x8

import led8x8motion

if __name__ == '__main__':
    LOCK = Lock()
    DISPLAY = BicolorMatrix8x8.BicolorMatrix8x8()
    CONTROLLER = led8x8motion.Led8x8Motion(DISPLAY, LOCK)
    CONTROLLER.reset()
    CONTROLLER.run()
    while True:
        choice = input("e, p > ")
        if choice == 'e' :
            print("exiting")
            break
        elif choice == "p":
        	CONTROLLER.motion_detected("perimeter/front/motion")

