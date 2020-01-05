#!/usr/bin/python3

""" Display War Games WOPR pattern on an Adafruit 8x8 LED backpack """

# MIT License
#
# Copyright (c) 2019 Dave Wilson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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

    def __init__(self, matrix8x8):
        """ create initial conditions and saving display and I2C lock """
        self.matrix = matrix8x8
        self.matrix.set_brightness(BRIGHTNESS)

    def reset(self,):
        """ initialize to starting state and set brightness """
        self.matrix.set_brightness(BRIGHTNESS)

    def output_row(self, start, finish, color):
        """ display a section of WOPR based on starting and ending rows """
        for xpixel in range(8):
            for ypixel in range(start, finish):
                bit = random.randint(0, 1)
                if bit == 0:
                    self.matrix.set_pixel(ypixel, xpixel, BLACK)
                    #self.matrix.set_pixel(xpixel, ypixel, BLACK)
                else:
                    self.matrix.set_pixel(ypixel, xpixel, color)
                    #self.matrix.set_pixel(xpixel, ypixel, color)

    def display(self,):
        """ display the series as a 64 bit image with alternating colored pixels """
        time.sleep(UPDATE_RATE_SECONDS)
        self.matrix.clear()
        self.output_row(0, 1, RED)
        self.output_row(1, 2, YELLOW)
        self.output_row(2, 4, RED)
        self.output_row(4, 5, YELLOW)
        self.output_row(5, 8, RED)
        self.matrix.write_display()

if __name__ == '__main__':
    exit()
