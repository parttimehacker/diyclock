#!/usr/bin/python3
""" Display full screen flash color pattern on an Adafruit 8x8 LED backpack """

import time
import random

BRIGHTNESS = 5

UPDATE_RATE_SECONDS = 0.2

BLACK = 0
GREEN = 1
YELLOW = 3
RED = 2

class Led8x8Wopr:
    """ WOPR pattern based on the movie Wargames """

    def __init__(self, matrix8x8, lock):
        """ create initial conditions and saving display and I2C lock """
        self.bus_lock = lock
        self.bus_lock.acquire(True)
        self.matrix = matrix8x8
        self.matrix.set_brightness(BRIGHTNESS)
        self.bus_lock.release()

    def reset(self,):
        """ initialize to starting state and set brightness """
        self.bus_lock.acquire(True)
        self.bus_lock.release()

    def output_row(self, start, finish, color):
        """ display a section of WOPR based on starting and ending rows """
        for xpixel in range(8):
            for ypixel in range(start, finish):
                bit = random.randint(0, 1)
                if bit == 0:
                    self.matrix.set_pixel(ypixel, xpixel, BLACK)
                else:
                    self.matrix.set_pixel(ypixel, xpixel, color)

    def display(self,):
        """ display the series as a 64 bit image with alternating colored pixels """
        time.sleep(UPDATE_RATE_SECONDS)
        self.bus_lock.acquire(True)
        self.output_row(0, 1, RED)
        self.output_row(1, 2, YELLOW)
        self.output_row(2, 4, RED)
        self.output_row(4, 5, YELLOW)
        self.output_row(5, 8, RED)
        self.matrix.write_display()
        self.bus_lock.release()

if __name__ == '__main__':
    exit()
