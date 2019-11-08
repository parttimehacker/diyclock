#!/usr/bin/python3
""" Test Bed for Diyhas System Status class """

import time
import datetime
from threading import Thread
import socket

import logging
import logging.config

from Adafruit_Python_LED_Backpack.Adafruit_LED_Backpack import SevenSegment

TIME_MODE = 0
WHO_MODE = 1
COUNT_MODE = 2

MAXIMUM_COUNT = 9999

logging.config.fileConfig(fname='/home/an/diyclock/logging.ini', disable_existing_loggers=False)

# Get the logger specified in the file
LOGGER = logging.getLogger(__name__)

LOGGER.info('Application started')

class TimeDisplay:
    """ display time """

    def __init__(self, display):
        """ initialize special feature and display format """
        self.seven_segment = display
        self.colon = False
        self.alarm = False
        self.time_format = "%l%M"

    def set_format(self, hour_format):
        """ set the time display in 12 or 24 hour format """
        self.time_format = hour_format

    def set_alarm(self, alarm):
        """ set alarm indictor pixel """
        self.alarm = alarm

    def display(self,):
        """ display time of day in 12 or 24 hour format """
        digit_string = time.strftime(self.time_format)
        try:
            self.seven_segment.clear()
            self.seven_segment.print_number_str(digit_string)
            self.seven_segment.set_colon(self.colon)
            if self.colon:
                self.colon = False
            else:
                self.colon = True
            self.seven_segment.set_decimal(3, self.alarm)
            now = datetime.datetime.now()
            if now.hour > 11:
                self.seven_segment.set_decimal(1, True)
            else:
                self.seven_segment.set_decimal(1, False)
            self.seven_segment.write_display()
        except Exception as e:
            LOGGER.error("Exception occurred", exc_info=True)

class WhoDisplay:
    """ display IP address in who mode """

    def __init__(self, display):
        """ prepare to show ip address on who message """
        self.seven_segment = display
        self.iterations = 0
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        host_ip = sock.getsockname()[0]
        sock.close()
        self.ip_address = host_ip.split(".")

    def display(self,):
        """ display 3 digits of ip address """
        try:
            self.seven_segment.clear()
            self.seven_segment.set_brightness(15)
            self.seven_segment.print_number_str(self.ip_address[self.iterations])
            self.iterations += 1
            if self.iterations >= 4:
                self.iterations = 0
            self.seven_segment.write_display()
        except Exception as e:
            LOGGER.error("Exception occurred", exc_info=True)

class CountdownDisplay:
    """ display countdown in countdown mode """

    def __init__(self, display):
        """ prepare to show counting down """
        self.seven_segment = display
        self.iterations = MAXIMUM_COUNT
        self.max_count = MAXIMUM_COUNT

    def display(self,):
        """ display 3 digits of ip address """
        self.iterations -= 1
        digits = '{0:d}'.format(self.iterations)
        try:
            self.seven_segment.print_number_str(digits)
            if self.iterations == 0:
                self.iterations = self.max_count
            self.seven_segment.write_display()
        except Exception as e:
            LOGGER.error("Exception occurred", exc_info=True)

    def set_maximum(self, new_maximum):
        """ set a new count down maximum less than 1000 """
        if new_maximum <= MAXIMUM_COUNT:
            self.iterations = new_maximum
            self.max_count = new_maximum

class LedClock:
    """ LED seven segment display object """

    def __init__(self,):
        """Create display instance on default I2C address (0x70) and bus number"""
        self.display = SevenSegment.SevenSegment(address=0x70)
        # Initialize the display. Must be called once before using the display.
        self.display.begin()
        self.brightness = 15
        self.display.set_brightness(self.brightness)
        self.display.set_blink(0)
        self.mode = TIME_MODE
        self.clock = TimeDisplay(self.display)
        self.who = WhoDisplay(self.display)
        self.count = CountdownDisplay(self.display)
        self.tu_thread = Thread(target=self.time_update_thread)
        self.tu_thread.daemon = True

    def time_update_thread(self,):
        """ print "started timeUpdateThread """
        while True:
            time.sleep(1.0)
            if self.mode == TIME_MODE:
                self.clock.display()
            elif self.mode == COUNT_MODE:
                self.count.display()
            else:
                self.who.display()

    def set_mode(self, mode):
        """ set alarm indicator """
        self.mode = mode

    def set_hour_format(self, hour_format=True):
        """ set 12 or 24 hour clock format """
        if hour_format:
            self.clock.set_format("%I%M")
        else:
            self.clock.set_format("%l%M")

    def set_alarm(self, alarm):
        """ set alarm indicator """
        self.clock.alarm = alarm

    def set_brightness(self, val):
        """ set brightness in range from 1 to 15 """
        # print("set brightness="+str(val))
        self.brightness = val
        self.display.set_brightness(self.brightness)

    def increase_brightness(self,):
        """ increase brightness by 1 """
        self.brightness = self.brightness + 1
        if self.brightness > 15:
            self.brightness = 15
        self.display.set_brightness(self.brightness)

    def decrease_brightness(self,):
        """ decrease brightness by 1 """
        self.brightness = self.brightness - 1
        if self.brightness < 0:
            self.brightness = 0
        self.display.set_brightness(self.brightness)

    def run(self,):
        """ start the clock thread """
        self.tu_thread.start()

if __name__ == '__main__':
    exit()
