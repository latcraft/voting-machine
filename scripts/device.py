#!/usr/bin/python

import sys
import signal
import logging
import time
import inspect

import RPi.GPIO as GPIO
import grovepi as Grove

from threading import Thread, Lock
from time import sleep

################################################################################
# LOGGING
################################################################################

logging.basicConfig(
  filename = '/var/log/device.log', 
  level    = logging.DEBUG, 
  format   = '%(asctime)s %(message)s', 
  datefmt  = '%Y-%m-%d %H:%M:%S'
)

################################################################################
# DATA
################################################################################

active    = True

################################################################################
# CLASSES
################################################################################

class Idler:

  @staticmethod
  def current_millis():
    return int(round(time.time() * 1000))

  def __init__(self, actions, timeout):
    self.name = 'Idler'
    self.timeout = timeout
    self.actions = actions
    self.idling = False
    self.idle_time = self.current_millis()
    self.__start()

  def stop_idling(self):
    self.idling = False
    self.__reset_idle_time()

  def __reset_idle_time(self):
    self.idle_time = self.current_millis()

  def __react(self):
    self.idling = True    
    if self.actions is not None:
      while self.idling:
        for action in self.actions:
          if self.idling:
            action()
          else:
            break        
    self.__reset_idle_time()

  def __idle_for_too_long(self):
    return self.current_millis() - self.idle_time > self.timeout

  def __idle(self):
    while active:
      if self.__idle_for_too_long():
        self.__react()
      sleep(5)

  def __start(self):
    thread = Thread(target = self.__idle)
    thread.daemon = True
    thread.start()


class Stats:

  def __init__(self):
    self.stats = {}
    self.lock = Lock()
    self.__start()
   
  def inc(self, counter):
    with self.lock:
      if not counter in self.stats:
        self.stats[counter] = 0
      self.stats[counter] += 1

  def __write(self):
    while active:
      if len(self.stats) > 0:
        with self.lock:
          logging.info('STATS: ' + (','.join(str(counter_name) + '=' + str(counter_value) for counter_name, counter_value in self.stats.iteritems())))
          for counter in self.stats:
            self.stats[counter] = 0
      sleep(60)
    
  def __start(self):
    thread = Thread(target = self.__write)
    thread.daemon = True
    thread.start()


class Button:

  def __init__(self, pin, name, action):
    self.pin = pin
    self.name = name
    self.action = action 
    self.__start()

  def __react(self):
    if self.action is not None:
      self.action(self)

  def __start(self):
    thread = Thread(target = self.__listen)
    thread.daemon = True
    thread.start()

  def __listen(self):
    GPIO.setup(self.pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    prev_input = GPIO.input(self.pin)
    while active:
      curr_input = GPIO.input(self.pin)
      if ((not prev_input) and curr_input):        
        self.__react()
      prev_input = curr_input
      sleep(0.05)    


################################################################################
# METHODS
################################################################################

def init_boards():
  GPIO.setwarnings(False)
  GPIO.cleanup()
  GPIO.setmode(GPIO.BCM)
   
def led_on(led_pin):
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(led_pin, GPIO.OUT)
  GPIO.output(led_pin, 0)
  GPIO.output(led_pin, 1)

def led_off(led_pin):
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(led_pin, GPIO.OUT)
  GPIO.output(led_pin, 0)

def leds_off(led_pins):
  GPIO.setmode(GPIO.BCM)
  for led_pin in led_pins:
    GPIO.setup(led_pin, GPIO.OUT)
    GPIO.output(led_pin, 0)

def grove_buzzer_on(buzzer):
  Grove.pinMode(buzzer, "OUTPUT")
  Grove.digitalWrite(buzzer, 1)

def grove_buzzer_off(buzzer):
  Grove.digitalWrite(buzzer, 0)

def log_action(device):
  logging.info(str(device.name) + ' activated')

def action(on_functions, off_functions, timeout, device):
  try:
    for on_function in on_functions:
      if device and len(inspect.getargspec(on_function).args) > 0:
        on_function(device)
      else:
        on_function()
    sleep(timeout)
  finally:
    for off_function in off_functions:
      if device and len(inspect.getargspec(off_function).args) > 0:
        off_function(device)
      else:
        off_function()

################################################################################
# MAIN
################################################################################

logging.info('Starting IOT service')

init_boards()

idling_steps = [
  lambda: led_on(17),
  lambda: sleep(0.1),
  lambda: led_off(17),
  lambda: sleep(0.1),
  lambda: led_on(27),
  lambda: sleep(0.1),
  lambda: led_off(27),
  lambda: sleep(0.1),
  lambda: led_on(22),
  lambda: sleep(0.1),
  lambda: led_off(22),
  lambda: sleep(0.1),
]

leds_off([17, 27, 22])
grove_buzzer_off(6)

stats = Stats()
idler = Idler(actions = idling_steps, timeout = 6000)

on_functions = [ lambda: idler.stop_idling(), log_action, lambda button: stats.inc(button.name), lambda: grove_buzzer_on(6) ]
off_functions = [ lambda: grove_buzzer_off(6), lambda: leds_off([17, 27, 22]) ]

Button(16, 'RED', lambda button: action(on_functions + [ lambda: led_on(17) ], off_functions, 0.1, button))
Button(20, 'YELLOW', lambda button: action(on_functions + [ lambda: led_on(27) ], off_functions, 0.1, button))
Button(21, 'GREEN', lambda button: action(on_functions + [ lambda: led_on(22) ], off_functions, 0.1, button))

logging.info('Started')

def signal_handler(signal, frame):
  logging.info('Ctrl+C was detected!')
  active = False
  idler.stop_idling()
  leds_off([17, 27, 22])
  grove_buzzer_off(6)
  logging.info('Stopped')
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to exit')
signal.pause()

