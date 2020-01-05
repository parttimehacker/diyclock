#!/usr/bin/python3
""" Display full screen flash color pattern on an Adafruit 8x8 LED backpack """

import time

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

    def __init__(self, matrix8x8):
        """ create initial conditions and saving display and I2C lock """
        self.matrix = matrix8x8
        # self.matrix.begin()
        self.matrix.set_brightness(BRIGHTNESS)
        self.matrix_image = Image.new('RGB', (8, 8))
        self.matrix_draw = ImageDraw.Draw(self.matrix_image)
        self.dispatch = {}
        self.motions = 0
        self.reset()

    def draw_two(self, color, row, column):
        """ display a small room or area """
        # print("draw_two color=",color)
        self.matrix_draw.line((row, column, row, column+1), fill=color)

    def draw_four(self, color, row, column):
        """ draw a medium or large area """
        # print("draw_four color=",color)
        self.matrix_draw.line((row, column, row, column+1), fill=color)
        self.matrix_draw.line((row+1, column, row+1, column+1), fill=color)

    def reset(self,):
        """ initialize to starting state and set brightness """
        self.motions = 8
        self.dispatch = {
            "diy/perimeter/front/motion":
                {"method": self.draw_two, "row" : 0, "column" : 3, "seconds" : 10},
            "diy/main/hallway/motion":
                {"method": self.draw_two, "row" : 2, "column" : 3, "seconds" : 10},
            "diy/main/dining/motion":
                {"method": self.draw_four, "row" : 3, "column" : 0, "seconds" : 10},
            "diy/main/garage/motion":
                {"method": self.draw_four, "row" : 0, "column" : 6, "seconds" : 10},
            "diy/main/living/motion":
                {"method": self.draw_four, "row" : 3, "column" : 6, "seconds" : 10},
            "diy/upper/guest/motion":
                {"method": self.draw_four, "row" : 6, "column" : 0, "seconds" : 10},
            "diy/upper/study/motion":
                {"method": self.draw_four, "row" : 6, "column" : 6, "seconds" : 10},
            "diy/upper/stairs/motion":
                {"method": self.draw_two, "row" : 5, "column" : 3, "seconds" : 10}
            }

    def display(self,):
        ''' display the series as a 64 bit image with alternating colored pixels '''
        time.sleep(UPDATE_RATE_SECONDS)
        self.matrix_draw.rectangle((0, 0, 7, 7), outline=(0, 0, 0), fill=(0, 0, 0))
        self.motions = 0
        for key in self.dispatch:
            self.dispatch[key]["seconds"] = self.dispatch[key]["seconds"] - 1
            if self.dispatch[key]["seconds"] > 50:
                self.motions += 1
                self.dispatch[key]["method"]((255, 0, 0),
                                             self.dispatch[key]["row"],
                                             self.dispatch[key]["column"])
            elif self.dispatch[key]["seconds"] > 30:
                self.motions += 1
                self.dispatch[key]["method"]((255, 255, 0),
                                             self.dispatch[key]["row"],
                                             self.dispatch[key]["column"])
            elif self.dispatch[key]["seconds"] > 0:
                self.motions += 1
                self.dispatch[key]["method"]((0, 255, 0),
                                             self.dispatch[key]["row"],
                                             self.dispatch[key]["column"])
            else:
                self.dispatch[key]["seconds"] = 0
        self.matrix.set_image(self.matrix_image)
        self.matrix.write_display()

    def motion_detected(self, topic):
        ''' set timer to countdown occupancy '''
        for key in self.dispatch:
            if key == topic:
                self.dispatch[key]["seconds"] = 60
                # print("motion_detected topic=",topic)

if __name__ == '__main__':
    exit()
