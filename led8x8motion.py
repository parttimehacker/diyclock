#!/usr/bin/python3
""" Display full screen flash color pattern on an Adafruit 8x8 LED backpack """

import time

from threading import Thread

from PIL import Image
from PIL import ImageDraw

BRIGHTNESS = 5

UPDATE_RATE_SECONDS = 1.0

BLACK = 0
GREEN = 1
YELLOW = 3
RED = 2

class Led8x8Motion:
    """ Display motion in various rooms of the house """

    def __init__(self, matrix8x8, lock):
        """ create initial conditions and saving display and I2C lock """
        self.bus_lock = lock
        self.bus_lock.acquire(True)
        self.matrix = matrix8x8
        self.matrix.set_brightness(BRIGHTNESS)
        self.matrix_image = Image.new('RGB', (8, 8))
        self.matrix_draw = ImageDraw.Draw(self.matrix_image)
        self.dispatch = {}
        self.bus_lock.release()

    def draw_two(self, color, row, column):
        """ display a small room or area """
        self.matrix_draw.line((row, column, row, column+1), fill=color)

    def draw_four(self, color, row, column):
        """ draw a medium or large area """
        self.matrix_draw.line((row, column, row, column+1), fill=color)
        self.matrix_draw.line((row+1, column, row+1, column+1), fill=color)

    def reset(self,):
        """ initialize to starting state and set brightness """
        self.bus_lock.acquire(True)
        self.dispatch = {
            "perimeter/front/motion":
                {"method": self.draw_two, "row" : 0, "column" : 3, "seconds" : 60},
            "main/hallway/motion":
                {"method": self.draw_two, "row" : 2, "column" : 3, "seconds" : 30},
            "main/dining/motion":
                {"method": self.draw_four, "row" : 3, "column" : 0, "seconds" : 60},
            "main/garage/motion":
                {"method": self.draw_four, "row" : 0, "column" : 6, "seconds" : 30},
            "main/living/motion":
                {"method": self.draw_four, "row" : 3, "column" : 6, "seconds" : 60},
            "upper/guest/motion":
                {"method": self.draw_four, "row" : 6, "column" : 0, "seconds" : 30},
            "upper/study/motion":
                {"method": self.draw_four, "row" : 6, "column" : 6, "seconds" : 60},
            "upper/stairs/motion":
                {"method": self.draw_two, "row" : 5, "column" : 3, "seconds" : 10}
            }
        self.bus_lock.release()

    def display(self,):
        """ display the series as a 64 bit image with alternating colored pixels """
        time.sleep(UPDATE_RATE_SECONDS)
        self.bus_lock.acquire(True)
        # self.matrix.clear()
        self.matrix.set_image(self.matrix_image)
        self.matrix.write_display()
        self.bus_lock.release()

    def display_thread(self,):
        """ display the series as a 64 bit image with alternating colored pixels """
        while True:
            time.sleep(UPDATE_RATE_SECONDS)
            self.bus_lock.acquire(True)
            self.matrix_draw.rectangle((0, 0, 7, 7), outline=(0, 0, 0), fill=(0, 0, 0))
            for key in self.dispatch:
                self.dispatch[key]["seconds"] = self.dispatch[key]["seconds"] - 1
                if self.dispatch[key]["seconds"] > 50:
                    self.dispatch[key]["method"]((255, 0, 0),
                                                 self.dispatch[key]["row"],
                                                 self.dispatch[key]["column"])
                elif self.dispatch[key]["seconds"] > 30:
                    self.dispatch[key]["method"]((255, 255, 0),
                                                 self.dispatch[key]["row"],
                                                 self.dispatch[key]["column"])
                elif self.dispatch[key]["seconds"] > 0:
                    self.dispatch[key]["method"]((0, 255, 0),
                                                 self.dispatch[key]["row"],
                                                 self.dispatch[key]["column"])
                else:
                    self.dispatch[key]["method"]((0, 0, 0),
                                                 self.dispatch[key]["row"],
                                                 self.dispatch[key]["column"])
                    self.dispatch[key]["seconds"] = 0
            self.bus_lock.release()


    def run(self):
        """ start the display thread and make it a daemon """
        display = Thread(target=self.display_thread)
        display.daemon = True
        display.start()

if __name__ == '__main__':
    exit()
