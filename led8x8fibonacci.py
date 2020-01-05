#!/usr/bin/python3
""" Display the fibonacci series as a 64 bit pattern on an Adafruit 8x8 LED backpack """

import time

BRIGHTNESS = 5

UPDATE_RATE_SECONDS = 0.2

LARGEST_64_BIT_FIBONACCI = 7540113804746346429

class Led8x8Fibonacci:
    """ fibinocci pattern from 1 to largest 64 bit representation  """

    def __init__(self, matrix8x8):
        """ create initial conditions and saving display and I2C lock """
        self.matrix = matrix8x8
        # self.matrix.begin()
        self.iterations = 0
        self.fib1 = 1
        self.fib2 = 1
        self.fib3 = 2

    def reset(self,):
        """ initialize to starting state and set brightness """
        self.iterations = 0
        self.fib1 = 1
        self.fib2 = 1
        self.fib3 = 2
        self.matrix.set_brightness(BRIGHTNESS)

    def display(self,):
        """ display the series as a 64 bit image with alternating colored pixels """
        time.sleep(UPDATE_RATE_SECONDS)
        for ypixel in range(0, 8):
            for xpixel in range(0, 8):
                self.iterations += 1
                if self.iterations >= 4:
                    self.iterations = 1
                reg = self.fib3 >> (8 * xpixel)
                bit = reg & (1 << ypixel)
                if bit == 0:
                    self.matrix.set_pixel(xpixel, ypixel, 0)
                else:
                    self.matrix.set_pixel(xpixel, ypixel, self.iterations)
        self.matrix.write_display()
        self.fib1 = self.fib2
        self.fib2 = self.fib3
        self.fib3 = self.fib1 + self.fib2
        if self.fib3 > LARGEST_64_BIT_FIBONACCI:
            self.fib1 = 1
            self.fib2 = 1
            self.fib3 = 2

if __name__ == '__main__':
    exit()
