#!/usr/bin/python3
""" Control the display of an Adafruit 8x8 LED backpack """

import time
from threading import Thread

import led8x8idle
import led8x8flash
import led8x8fibonacci
import led8x8motion
import led8x8wopr
import led8x8life

# Color values as convenient globals.
OFF = 0
GREEN = 1
RED = 2
YELLOW = 3

# modes as convenient globals
IDLE_MODE = 0
FIRE_MODE = 1
PANIC_MODE = 2
FIBONACCI_MODE = 3
WOPR_MODE = 4
LIFE_MODE = 5
MOTION_MODE = 6

class ModeController:
    """ control changing modes. note Fire and Panic are externally controlled. """

    def __init__(self, lock):
        """ create mode control variables """
        self.bus_lock = lock
        self.current_mode = FIBONACCI_MODE
        self.last_mode = LIFE_MODE
        self.start_time = time.time()

    def set(self, mode):
        """ set or override the mode """
        self.bus_lock.acquire(True)
        self.last_mode = self.current_mode
        self.current_mode = mode
        self.start_time = time.time()
        self.bus_lock.release()

    def restore(self,):
        """ set or override the mode """
        self.bus_lock.acquire(True)
        self.current_mode = self.last_mode
        self.start_time = time.time()
        self.bus_lock.release()

    def get(self,):
        return self.current_mode

    def evaluate(self,):
        """ initialize and start the fibinnocci display """
        self.bus_lock.acquire(True)
        if self.current_mode != FIRE_MODE:
            if self.current_mode != PANIC_MODE:
                if self.current_mode != IDLE_MODE:
                    now_time = time.time()
                    elapsed = now_time - self.start_time
                    if elapsed > 30:
                        self.last_mode = self.current_mode
                        self.current_mode = self.current_mode + 1
                        self.start_time = now_time
                        if self.current_mode > LIFE_MODE:
                            self.current_mode = FIBONACCI_MODE
        self.bus_lock.release()


class Led8x8Controller:
    """ Idle or sleep pattern """

    def __init__(self, matrix8x8, lock):
        """ create initial conditions and saving display and I2C lock """
        self.bus_lock = lock
        self.matrix8x8 = matrix8x8
        self.mode_controller = ModeController(self.bus_lock)
        self.idle = led8x8idle.Led8x8Idle(self.matrix8x8, self.bus_lock)
        self.fire = led8x8flash.Led8x8Flash(self.matrix8x8, self.bus_lock, RED)
        self.panic = led8x8flash.Led8x8Flash(self.matrix8x8, self.bus_lock, YELLOW)
        self.fib = led8x8fibonacci.Led8x8Fibonacci(self.matrix8x8, self.bus_lock)
        self.motion = led8x8motion.Led8x8Motion(self.matrix8x8, self.bus_lock)
        self.wopr = led8x8wopr.Led8x8Wopr(self.matrix8x8, self.bus_lock)
        self.life = led8x8life.Led8x8Life(self.matrix8x8, self.bus_lock)

    def reset(self,):
        """ initialize to starting state and set brightness """
        self.bus_lock.acquire(True)
        self.bus_lock.release()

    def display_thread(self,):
        """ display the series as a 64 bit image with alternating colored pixels """
        while True:
            mode = self.mode_controller.get()
            if mode == IDLE_MODE:
                self.idle.display()
            elif mode == FIRE_MODE:
                self.fire.display()
            elif mode == PANIC_MODE:
                self.panic.display()
            elif mode == FIBONACCI_MODE:
                self.fib.display()
            elif mode == MOTION_MODE:
                self.motion.display()
                if self.motion.motions == 0:
                	self.restore_mode()
            elif mode == WOPR_MODE:
                self.wopr.display()
            elif mode == LIFE_MODE:
                self.life.display()
            self.mode_controller.evaluate()

    def set_mode(self, mode, override=False, option=""):
        """ set display mode """
        if override:
            self.mode_controller.set(mode)
        current_mode = self.mode_controller.get()
        if current_mode == FIRE_MODE or current_mode == PANIC_MODE:
            return
        self.mode_controller.set(mode)
        if mode == MOTION_MODE:
            self.motion.motion_detected(option)


    def restore_mode(self,):
        """ return to last mode; usually after idle, fire or panic """
        self.bus_lock.acquire(True)
        self.mode = self.last_mode
        self.bus_lock.release()

    def run(self):
        """ start the display thread and make it a daemon """
        display = Thread(target=self.display_thread)
        display.daemon = True
        display.start()

if __name__ == '__main__':
    exit()
