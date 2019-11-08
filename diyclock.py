#!/usr/bin/python3
""" Diyhas clock, motion detector and piezo alarm """

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

class MqttTopicConfiguration:
    """ motion_topic to avoid global PEP8 """

    def __init__(self):
        """ create two topics for this application """
        self.setup_topic = "diyhas/" + socket.gethostname() + "/setup"
        self.motion_topic = ""
    def set(self, topic):
        """ the motion topic is passed to the app at startup """
        self.motion_topic = topic
    def get_setup(self,):
        """ the motion topic dynamically set """
        return self.setup_topic
    def get_motion(self,):
        """ the motion topic dynamically set """
        return self.motion_topic

MOTION_TOPIC = MqttTopicConfiguration()

class MotionController:
    """ motion detection device driver """

    def __init__(self, pin):
        """ capture interrupts on pin 17  """
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

DISPLAY = BicolorMatrix8x8.BicolorMatrix8x8(address=0x71)

MATRIX = led8x8controller.Led8x8Controller(DISPLAY)
MATRIX.run()

ALARM = AlarmController(4)
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
            CLOCK.set_brightness(15)
            MATRIX.set_mode(led8x8controller.FIBONACCI_MODE)
            self.lights_are_on = True
        else:
            CLOCK.set_brightness(2)
            MATRIX.set_mode(led8x8controller.IDLE_MODE)
            self.lights_are_on = False

    def check_for_timed_events(self,):
        """ turn down displays at night """
        now = datetime.datetime.now().time()
        if now < self.day:
            if self.lights_are_on:
                self.control_lights("Turn Off")
        elif now > self.night:
            if self.lights_are_on:
                self.control_lights("Turn Off")
        else:
            if not self.lights_are_on:
                self.control_lights("Turn On")

DAY_DEFAULT = datetime.time(5, 1)
NIGHT_DEFAULT = datetime.time(21, 1)
TIMER = TimedEvents(DAY_DEFAULT, NIGHT_DEFAULT)

def system_message(msg):
    """ process system messages"""
    LOGGER.info(msg.topic+" "+msg.payload.decode('utf-8'))
    if msg.topic == 'diyhas/system/fire':
        if msg.payload == b'ON':
            MATRIX.set_mode(led8x8controller.FIRE_MODE)
            ALARM.sound_alarm(True)
        else:
            MATRIX.set_mode(led8x8controller.FIBONACCI_MODE, True)
            ALARM.sound_alarm(False)
    elif msg.topic == 'diyhas/system/panic':
        if msg.payload == b'ON':
            MATRIX.set_mode(led8x8controller.PANIC_MODE)
            ALARM.sound_alarm(True)
        else:
            MATRIX.set_mode(led8x8controller.FIBONACCI_MODE, True)
            ALARM.sound_alarm(False)
    elif msg.topic == 'diyhas/system/who':
        if msg.payload == b'ON':
            CLOCK.set_mode(ledclock.WHO_MODE)
        else:
            CLOCK.set_mode(ledclock.TIME_MODE)
    elif msg.topic == 'diyhas/system/security':
        if msg.payload == b'ON':
            MATRIX.set_security("ON")
        else:
            MATRIX.set_security("OFF")
    elif msg.topic == MOTION_TOPIC.get_setup():
        topic = msg.payload.decode('utf-8') + "/motion"
        MOTION_TOPIC.set(topic)


# use a dispatch model for the subscriptions
TOPIC_DISPATCH_DICTIONARY = {
    "diyhas/system/security":
        {"method":system_message},
    "diyhas/system/fire":
        {"method":system_message},
    "diyhas/system/panic":
        {"method":system_message},
    "diyhas/system/who":
        {"method":system_message},
    MOTION_TOPIC.get_setup():
        {"method":system_message}
    }


# The callback for when the client receives a CONNACK response from the server.
# def on_connect(client, userdata, flags, rc):
def on_connect(client, userdata, flags, rc):
    """ Subscribing in on_connect() means that if we lose the connection and
        reconnect then subscriptions will be renewed. """
    client.subscribe("diyhas/system/security", 1)
    client.subscribe("diyhas/system/fire", 1)
    client.subscribe("diyhas/system/panic", 1)
    client.subscribe("diyhas/system/who", 1)
    client.subscribe(MOTION_TOPIC.get_setup(), 1)
    client.subscribe("diyhas/+/+/motion", 1)

def on_disconnect(client, userdata, rc):
    LOGGER.info("disconnecting reason  "+str(rc))
    client.connected_flag=False
    client.disconnect_flag=True


# The callback for when a PUBLISH message is received from the server.
# def on_message(client, userdata, msg):
def on_message(client, userdata, msg):
    """ dispatch to the appropriate MQTT topic handler """
    if "motion" in msg.topic:
        MATRIX.set_mode(led8x8controller.MOTION_MODE, option=msg.topic)
    TOPIC_DISPATCH_DICTIONARY[msg.topic]["method"](msg)

MOTION = MotionController(17)
MOTION.enable()

if __name__ == '__main__':
    #Start utility threads, setup MQTT handlers then wait for timed events

    CLIENT = mqtt.Client()
    CLIENT.on_connect = on_connect
    CLIENT.on_disconnect = on_disconnect
    CLIENT.on_message = on_message
    CLIENT.connect("192.168.1.17", 1883, 60)
    CLIENT.loop_start()

    # give network time to startup - hack?
    time.sleep(1.0)

    # loop forever checking for interrupts or timed events

    while True:
        time.sleep(0.5)
        if MOTION.detected():
            VALUE = MOTION.get_motion()
            TOPIC = MOTION_TOPIC.get_motion()
            CLIENT.publish(TOPIC, VALUE, 0, True)
        TIMER.check_for_timed_events()
