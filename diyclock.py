#!/usr/bin/python3
''' Diyhas clock, motion detector and piezo alarm '''

import time
import datetime
import socket
import queue

from threading import Lock

import paho.mqtt.client as mqtt

from Adafruit_Python_GPIO.Adafruit_GPIO import GPIO

from ledclock import *
from ledmatrix8x8 import *

class MqttTopicConfiguration:
    ''' motion_topic to avoid global PEP8 '''
    def __init__(self):
        ''' create two topics for this application '''
        self.setup_topic = "diyhas/" + socket.gethostname() + "/setup"
        self.motion_topic = ""
    def set(self, topic):
        ''' the motion topic is passed to the app at startup '''
        print("set motion_topic=", topic)
        self.motion_topic = topic
    def get_setup(self,):
        ''' the motion topic dynamically set '''
        return self.setup_topic
    def get_motion(self,):
        ''' the motion topic dynamically set '''
        return self.motion_topic

MOTION_TOPIC = MqttTopicConfiguration()

class MotionController:
    ''' motion detection device driver '''
    def __init__(self, pin):
        ''' capture interrupts on pin 17  '''
        self.gpio = GPIO.get_platform_gpio()
        self.queue = queue.Queue()
        self.pin = pin
        self.gpio.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def pir_interrupt_handler(self, gpio):
        ''' motion interrupt handler sends 1 or 0 to queue '''
        state = self.gpio.input(gpio)
        if state == 1:
            message = "1"
        else:
            message = "0"
        self.queue.put(message)

    def enable(self,):
        ''' enable the interrupt handler '''
        self.gpio.add_event_detect(self.pin, GPIO.RISING, callback=self.pir_interrupt_handler)

    def detected(self,):
        ''' has motion been detected '''
        return not self.queue.empty()

    def get_motion(self,):
        ''' return the last value either 1 or 0 '''
        return self.queue.get(False)

    def wait_for_motion(self,):
        ''' wait for the next interrupt 1 or 0 '''
        return self.queue.get(True)

class AlarmController:
    ''' alarm piezo device driver '''
    def __init__(self, pin):
        ''' control output to pin 4  '''
        self.gpio = GPIO.get_platform_gpio()
        self.pin = pin
        self.gpio.setup(self.pin, GPIO.OUT)
        self.gpio.output(self.pin, GPIO.LOW)

    def sound_alarm(self, turn_on):
        if turn_on:
            self.gpio.output(self.pin, GPIO.HIGH)
        else:
            self.gpio.output(self.pin, GPIO.LOW)

# create lock to coordinate I2C communication and start displays
BUSLOCK = Lock()

CLOCK = LedClock(BUSLOCK)
CLOCK.run()

MATRIX = LedMatrix8x8(BUSLOCK)
MATRIX.run()

ALARM = AlarmController(4)
ALARM.sound_alarm(False)


class TimedEvents:
    ''' timed event handler '''

    def __init__(self, day, night):
        ''' initialize night,day and light status '''
        if night < day:
            raise "NIGHT < DAY"
        self.night = night
        self.day = day
        self.lights_are_on = True

    def control_lights(self,switch):
        ''' dim lights at night or turn up during the day '''
        if switch == "Turn On":
            CLOCK.set_brightness(15)
            MATRIX.set_mode(FIBINACCI_MODE)
            self.lights_are_on = True
        else:
            CLOCK.set_brightness(2)
            MATRIX.set_mode(IDLE_MODE)
            self.lights_are_on = False

    def check_for_timed_events(self,):
        ''' turn down displays at night '''
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

DAY_DEFAULT = datetime.time(5,1)
NIGHT_DEFAULT = datetime.time(21,1)
TIMER = TimedEvents(DAY_DEFAULT,NIGHT_DEFAULT)

def system_message(msg):
    ''' process system messages'''
    print("msg.payload=", msg.payload)
    if msg.topic == 'diyhas/system/fire':
        if msg.payload == b'ON':
            print("fire ON")
            MATRIX.set_mode(FIRE_MODE)
            ALARM.sound_alarm(True)
        else:
            print("fire OFF")
            MATRIX.set_mode(FIBINACCI_MODE, True)
            ALARM.sound_alarm(False)
    elif msg.topic == 'diyhas/system/panic':
        if msg.payload == b'ON':
            print("panic ON")
            MATRIX.set_mode(PANIC_MODE)
            ALARM.sound_alarm(True)
        else:
            print("panic OFF")
            MATRIX.set_mode(FIBINACCI_MODE, True)
            ALARM.sound_alarm(False)
    elif msg.topic == 'diyhas/system/who':
        if msg.payload == b'ON':
            print("who ON")
            CLOCK.set_mode(WHO_MODE)
        else:
            print("who OFF")
            CLOCK.set_mode(TIME_MODE)
    elif msg.topic == MOTION_TOPIC.get_setup():
        print("motion topic=", msg.topic, " payload=", msg.payload)
        topic = msg.payload.decode('utf-8') + "/motion"
        MOTION_TOPIC.set(topic)


# use a dispatch model for the subscriptions
TOPIC_DISPATCH_DICTIONARY = {
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
def on_connect(client, userdata, flags, rc):
    ''' Subscribing in on_connect() means that if we lose the connection and
        reconnect then subscriptions will be renewed. '''
    client.subscribe("diyhas/system/fire", 1)
    client.subscribe("diyhas/system/panic", 1)
    client.subscribe("diyhas/system/who", 1)
    client.subscribe(MOTION_TOPIC.get_setup(), 1)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    ''' dispatch to the appropriate MQTT topic handler '''
    TOPIC_DISPATCH_DICTIONARY[msg.topic]["method"](msg)

MOTION = MotionController(17)
MOTION.enable()

if __name__ == '__main__':
    #Start utility threads, setup MQTT handlers then wait for timed events

    CLIENT = mqtt.Client()
    CLIENT.on_connect = on_connect
    CLIENT.on_message = on_message
    CLIENT.connect("192.168.1.xxx", 1883, 60)
    CLIENT.loop_start()

    # give network time to startup - hack?
    time.sleep(1.0)

    # loop forever checking for interrupts or timed events

    while True:
        time.sleep(0.5)
        if MOTION.detected():
            VALUE = MOTION.get_motion()
            CLIENT.publish(MOTION_TOPIC.get_motion(), VALUE, 0, True)
        TIMER.check_for_timed_events()
