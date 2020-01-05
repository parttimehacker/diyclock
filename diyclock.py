#!/usr/bin/python3

""" Diyhas clock, motion detector and piezo alarm """

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
import datetime
import socket
import queue
import logging
import logging.config

import paho.mqtt.client as mqtt

from Adafruit_GPIO import GPIO
from Adafruit_LED_Backpack import BicolorMatrix8x8

import ledclock

import led8x8controller

logging.config.fileConfig(fname='/home/an/diyclock/logging.ini', disable_existing_loggers=False)

# Get the logger specified in the file
LOGGER = logging.getLogger("diyclock")
LOGGER.info('Application started')

class Configuration:
    """ motion_topic to avoid global PEP8 """

    def __init__(self):
        """ create two topics for this application """
        self.setup_topic = "diy/" + socket.gethostname() + "/setup"
        self.motion_topic = ""
        self.pir_pin = 24
        self.piezo_pin = 4
        self.mqtt_ip = "192.168.1.53"
        self.matrix8x8_addr = 0x70
    def set(self, topic):
        """ the motion topic is passed to the app at startup """
        self.motion_topic = topic
    def get_setup(self,):
        """ the motion topic dynamically set """
        return self.setup_topic
    def get_motion(self,):
        """ the motion topic dynamically set """
        return self.motion_topic

CONFIG = Configuration()

class MotionController:
    """ motion detection device driver """

    def __init__(self, pin):
        """ capture interrupts """
        self.gpio = GPIO.get_platform_gpio()
        self.queue = queue.Queue()
        self.pin = pin
        self.gpio.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.last_reading = 0

    def pir_interrupt_handler(self, gpio):
        """ motion interrupt handler sends 1 or 0 to queue """
        state = self.gpio.input(gpio)
        if state == 1:
            message = "1"
        else:
            message = "0"
        if state != self.last_reading:
            self.queue.put(message)
        self.last_reading = state

    def enable(self,):
        """ enable the interrupt handler """
        self.gpio.add_event_detect(self.pin, GPIO.RISING, callback=self.pir_interrupt_handler)

    def detected(self,):
        """ has motion been detected """
        return not self.queue.empty()

    def get_motion(self,):
        """ return the last value either 1 or 0 """
        return self.queue.get(False)

    def wait_for_motion(self,):
        """ wait for the next interrupt 1 or 0 """
        return self.queue.get(True)

class AlarmController:
    """ alarm piezo device driver """
    def __init__(self, pin):
        """ control output to pin 4  """
        self.gpio = GPIO.get_platform_gpio()
        self.pin = pin
        self.gpio.setup(self.pin, GPIO.OUT)
        self.gpio.output(self.pin, GPIO.LOW)

    def sound_alarm(self, turn_on):
        """ turn power to piexo on or off """
        if turn_on:
            self.gpio.output(self.pin, GPIO.HIGH)
        else:
            self.gpio.output(self.pin, GPIO.LOW)

    def reset(self,):
        """ turn power to piexo off """
        self.gpio.output(self.pin, GPIO.LOW)

CLOCK = ledclock.LedClock()
CLOCK.run()

DISPLAY = BicolorMatrix8x8.BicolorMatrix8x8(address=CONFIG.matrix8x8_addr)
DISPLAY.begin()

MATRIX = led8x8controller.Led8x8Controller(DISPLAY)
MATRIX.run()

ALARM = AlarmController(CONFIG.piezo_pin)
ALARM.sound_alarm(False)


class TimedEvents:
    """ timed event handler """

    def __init__(self, day, night):
        """ initialize night,day and light status """
        if night < day:
            raise "NIGHT < DAY"
        self.night = night
        self.day = day
        self.lights_are_on = True

    def control_lights(self, switch):
        """ dim lights at night or turn up during the day """
        if switch == "Turn On":
            CLOCK.set_brightness(12)
            MATRIX.set_mode(led8x8controller.FIBONACCI_MODE)
            self.lights_are_on = True
        else:
            CLOCK.set_brightness(0)
            MATRIX.set_state(led8x8controller.IDLE_STATE)
            self.lights_are_on = False

    def check_for_timed_events(self,):
        """ turn down displays at night """
        now = datetime.datetime.now().time()
        if now <= self.day:
            if self.lights_are_on:
                self.control_lights("Turn Off")
        elif now >= self.night:
            if self.lights_are_on:
                self.control_lights("Turn Off")
        else:
            if not self.lights_are_on:
                self.control_lights("Turn On")

DAY_DEFAULT = datetime.time(6, 1)
NIGHT_DEFAULT = datetime.time(20, 1)
TIMER = TimedEvents(DAY_DEFAULT, NIGHT_DEFAULT)

def system_message(msg):
    """ process system messages"""
    #pylint: disable=too-many-branches
    #LOGGER.info(msg.topic+" "+msg.payload.decode('utf-8'))
    if msg.topic == 'diy/system/fire':
        if msg.payload == b'ON':
            MATRIX.set_mode(led8x8controller.FIRE_MODE)
            ALARM.sound_alarm(True)
        else:
            MATRIX.set_mode(led8x8controller.FIBONACCI_MODE, True)
            ALARM.sound_alarm(False)
    elif msg.topic == 'diy/system/panic':
        if msg.payload == b'ON':
            MATRIX.set_mode(led8x8controller.PANIC_MODE)
            ALARM.sound_alarm(True)
        else:
            MATRIX.set_mode(led8x8controller.FIBONACCI_MODE, True)
            ALARM.sound_alarm(False)
    elif msg.topic == 'diy/system/who':
        if msg.payload == b'ON':
            CLOCK.set_mode(ledclock.WHO_MODE)
        else:
            CLOCK.set_mode(ledclock.TIME_MODE)
    elif msg.topic == 'diy/system/demo':
        if msg.payload == b'ON':
            MATRIX.set_state(led8x8controller.DEMO_STATE)
        else:
            MATRIX.set_state(led8x8controller.IDLE_STATE)
    elif msg.topic == 'diy/system/security':
        if msg.payload == b'ON':
            MATRIX.set_state(led8x8controller.SECURITY_STATE)
        else:
            MATRIX.set_state(led8x8controller.DEMO_STATE)
    elif msg.topic == 'diy/system/silent':
        if msg.payload == b'ON':
            MATRIX.set_state(led8x8controller.IDLE_STATE)
        else:
            MATRIX.set_state(led8x8controller.DEMO_STATE)
    elif msg.topic == CONFIG.get_setup():
        topic = msg.payload.decode('utf-8') + "/motion"
        CONFIG.set(topic)


# use a dispatch model for the subscriptions
TOPIC_DISPATCH_DICTIONARY = {
    "diy/system/demo":
        {"method":system_message},
    "diy/system/fire":
        {"method":system_message},
    "diy/system/panic":
        {"method":system_message},
    "diy/system/security":
        {"method":system_message},
    "diy/system/silent":
        {"method":system_message},
    "diy/system/who":
        {"method":system_message},
    CONFIG.get_setup():
        {"method":system_message}
    }


# The callback for when the client receives a CONNACK response from the server.
# def on_connect(client, userdata, flags, rc):
def on_connect(client, userdata, flags, rcdata):
    #pylint: disable=unused-argument
    """ Subscribing in on_connect() means that if we lose the connection and
        reconnect then subscriptions will be renewed. """
    client.subscribe("diy/system/demo", 1)
    client.subscribe("diy/system/fire", 1)
    client.subscribe("diy/system/panic", 1)
    client.subscribe("diy/system/security", 1)
    client.subscribe("diy/system/silent", 1)
    client.subscribe("diy/system/who", 1)
    client.subscribe(CONFIG.get_setup(), 1)
    client.subscribe("diy/+/+/motion", 1)

def on_disconnect(client, userdata, rcdata):
    #pylint: disable=unused-argument
    """ disconnect detected """
    LOGGER.info("Disconnected")
    client.connected_flag = False
    client.disconnect_flag = True


# The callback for when a PUBLISH message is received from the server.
# def on_message(client, userdata, msg):
def on_message(client, userdata, msg):
    #pylint: disable=unused-argument
    """ dispatch to the appropriate MQTT topic handler """
    if "motion" in msg.topic:
        MATRIX.update_motion(msg.topic)
    else:
        TOPIC_DISPATCH_DICTIONARY[msg.topic]["method"](msg)

MOTION = MotionController(CONFIG.pir_pin)
MOTION.enable()

if __name__ == '__main__':
    #Start utility threads, setup MQTT handlers then wait for timed events

    CLIENT = mqtt.Client()
    CLIENT.on_connect = on_connect
    CLIENT.on_disconnect = on_disconnect
    CLIENT.on_message = on_message
    CLIENT.connect(CONFIG.mqtt_ip, 1883, 60)
    CLIENT.loop_start()

    # give network time to startup - hack?
    time.sleep(1.0)

    # loop forever checking for interrupts or timed events

    while True:
        time.sleep(1.0)
        if MOTION.detected():
            VALUE = MOTION.get_motion()
            TOPIC = CONFIG.get_motion()
            CLIENT.publish(TOPIC, VALUE, 0, True)
            # print("bil: motion detected")
        TIMER.check_for_timed_events()
