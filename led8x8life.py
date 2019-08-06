#!/usr/bin/python3
""" Display the Game of Life pattern on an Adafruit 8x8 LED backpack """

import time

BRIGHTNESS = 5

UPDATE_RATE_SECONDS = 0.3

PATTERN_RATE = 10

BLACK = 0
GREEN = 1
YELLOW = 3
RED = 2

class Led8x8Life:
    """ Game of Life pattern based on john Conway """

    def __init__(self, matrix8x8):
        """ create initial conditions and saving display and I2C lock """
        self.matrix = matrix8x8
        self.matrix.set_brightness(BRIGHTNESS)
        self.current_gen = [[0 for x in range(8)] for y in range(8)]
        self.next_gen = [[0 for x in range(8)] for y in range(8)]
        self.pattern = 0
        self.pattern_switch_time = time.time()
        self.dispatch = {
            0: self.glider,
            1: self.oscilator1,
            2: self.oscilator1,
            3: self.oscilator2,
            4: self.oscilator3,
            5: self.toad
        }

    def glider(self,):
        """ initialize to starting state and set brightness """
        self.next_gen[0] = [0, 0, 1, 0, 0, 0, 0, 0]
        self.next_gen[1] = [0, 0, 0, 1, 0, 0, 0, 0]
        self.next_gen[2] = [0, 1, 1, 1, 0, 0, 0, 0]
        self.next_gen[3] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.next_gen[4] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.next_gen[5] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.next_gen[6] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.next_gen[7] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.copy()

    def oscilator1(self,):
        """ initialize to starting state and set brightness """
        self.next_gen[0] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.next_gen[1] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.next_gen[2] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.next_gen[3] = [0, 1, 1, 1, 1, 1, 0, 0]
        self.next_gen[4] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.next_gen[5] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.next_gen[6] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.next_gen[7] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.copy()

    def oscilator2(self,):
        """ initialize to starting state and set brightness """
        self.next_gen[0] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.next_gen[1] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.next_gen[2] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.next_gen[3] = [0, 1, 1, 1, 1, 1, 1, 0]
        self.next_gen[4] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.next_gen[5] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.next_gen[6] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.next_gen[7] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.copy()

    def oscilator3(self,):
        """ initialize to starting state and set brightness """
        self.next_gen[0] = [0, 0, 0, 0, 0, 1, 1, 1]
        self.next_gen[1] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.next_gen[2] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.next_gen[3] = [0, 0, 0, 1, 1, 0, 0, 0]
        self.next_gen[4] = [0, 0, 0, 1, 0, 0, 0, 0]
        self.next_gen[5] = [0, 0, 0, 0, 0, 0, 1, 0]
        self.next_gen[6] = [0, 0, 0, 0, 0, 1, 1, 0]
        self.next_gen[7] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.copy()

    def toad(self,):
        """ initialize to starting state and set brightness """
        self.next_gen[0] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.next_gen[1] = [0, 0, 0, 1, 0, 0, 0, 0]
        self.next_gen[2] = [0, 1, 0, 0, 1, 0, 0, 0]
        self.next_gen[3] = [0, 1, 0, 0, 1, 0, 0, 0]
        self.next_gen[4] = [0, 0, 1, 0, 0, 0, 0, 0]
        self.next_gen[5] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.next_gen[6] = [0, 0, 0, 0, 1, 1, 1, 0]
        self.next_gen[7] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.copy()

    def spawn(self,):
        """ initialize to starting state and set brightness """
        self.dispatch[self.pattern]()
        self.pattern_switch_time = time.time()
        self.pattern += 1
        if self.pattern > 5:
            self.pattern = 0

    def reset(self,):
        """ initialize to starting state and set brightness """
        self.spawn()

    @classmethod
    def mod(cls, test):
        """ ensure that the returned coordinate is between 0 and 7 """
        safe = (test + 8) % 8
        return safe

    def draw(self,):
        """ display a section of WOPR based on starting and ending rows """
        for xpixel in range(8):
            for ypixel in range(8):
                color = BLACK
                if self.next_gen[xpixel][ypixel] >= 5:
                    color = RED
                elif self.next_gen[xpixel][ypixel] == 1:
                    color = GREEN
                elif self.next_gen[xpixel][ypixel] != 0:
                    color = YELLOW
                self.matrix.set_pixel(xpixel, ypixel, color)
        self.matrix.write_display()

    def age(self,):
        """ ensure that the returned coordinate is between 0 and 7 """
        for i in range(8):
            for j in range(8):
                alive = 0
                alive += self.current_gen[self.mod(i+1)][self.mod(j)] != 0
                alive += self.current_gen[self.mod(i)][self.mod(j+1)] != 0
                alive += self.current_gen[self.mod(i-1)][self.mod(j)] != 0
                alive += self.current_gen[self.mod(i)][self.mod(j-1)] != 0
                alive += self.current_gen[self.mod(i+1)][self.mod(j+1)] != 0
                alive += self.current_gen[self.mod(i-1)][self.mod(j-1)] != 0
                alive += self.current_gen[self.mod(i+1)][self.mod(j-1)] != 0
                alive += self.current_gen[self.mod(i-1)][self.mod(j+1)] != 0
                if self.current_gen[i][j] != 0:
                    if (alive < 2) or (alive > 3):
                        self.next_gen[i][j] = 0
                    else:
                        self.next_gen[i][j] = self.current_gen[i][j] + 1
                else:
                    if alive == 3:
                        self.next_gen[i][j] = 1

    def copy(self,):
        """ ensure that the returned coordinate is between 0 and 7 """
        early_spawn = True
        for i in range(8):
            for j in range(8):
                self.current_gen[i][j] = self.next_gen[i][j]
                if early_spawn:
                    if self.current_gen[i][j] != 0:
                        early_spawn = False
        if early_spawn:
            self.matrix.clear()
            self.matrix.write_display()
            self.spawn()
            time.sleep(1)

    def display(self,):
        """ display the series as a 64 bit image with alternating colored pixels """
        time.sleep(UPDATE_RATE_SECONDS)
        self.draw()
        self.age()
        self.copy()
        now_time = time.time()
        elapsed = now_time - self.pattern_switch_time
        if elapsed > PATTERN_RATE:
            self.spawn()

if __name__ == '__main__':
    exit()
