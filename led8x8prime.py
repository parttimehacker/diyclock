#!/usr/bin/python3
""" Test Bed for Diyhas System Status class """

import time

BRIGHTNESS = 10

UPDATE_RATE_SECONDS = 0.2

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67,
          71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149,
          151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
          233, 239, 241, 251]

class Led8x8Prime:
    """ Prime numbers less than 256 display on an 8x8 matrix """

    def __init__(self, matrix8x8):
        """ create the prime object """
        self.matrix = matrix8x8
        self.index = 0
        self.row = 0
        self.iterations = 0

    def reset(self,):
        """ initialize and start the prime number display """
        self.index = 0
        self.row = 0
        self.iterations = 0
        self.matrix.set_brightness(BRIGHTNESS)

    def display(self,):
        """ display primes up to the max for 8 bits """
        time.sleep(UPDATE_RATE_SECONDS)
        self.matrix.clear()
        # cycle through the primes
        self.index += 1
        if self.index >= len(PRIMES):
            self.index = 0
            self.row = 0
        number = PRIMES[self.index]
        #display 8 bit prime per row
        row = self.row
        self.row += 1
        if self.row >= 8:
            self.row = 0
        for xpixel in range(0, 8):
            bit = number & (1 << xpixel)
            if self.iterations == 3:
                self.iterations = 1
            else:
                self.iterations += 1
            if bit == 0:
                self.matrix.set_pixel(row, xpixel, 0)
            else:
                self.matrix.set_pixel(row, xpixel, self.iterations)
        self.matrix.write_display()

if __name__ == '__main__':
    exit()
