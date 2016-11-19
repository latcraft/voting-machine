#!/usr/bin/python

import sys
import signal
import usb
import nfc
import yaml
import logging
import time
import datetime

import RPi.GPIO as GPIO
import grovepi as Grove

from piglow import PiGlow
from threading import Thread
from time import sleep
from functools import partial

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
config    = None
stats     = {}

with open('/etc/device.yaml', 'r') as f:
  config = yaml.load(f)

################################################################################
# CLASSES
################################################################################

class Idler:

  def __init__(self, action, timeout):
    self.timeout = timeout
    self.action = action
    self.idle_time = current_millis()
    self.__start()

  def current_millis():
    return int(round(time.time() * 1000))

  def reset_idle_time(self):
    self.idle_time = current_millis()

  def __react(self):
    if self.action is not None:
      self.action(self)

  def __idle_for_too_long(self):
    return current_millis() - self.idle_time > self.timeout

  def __idle(self):
    while True:
      if __idle_for_too_long():
        self.__react()
        self.__reset_idle()
      sleep(20)

  def __start():
    thread = Thread(target = __idle, args = (self))
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
    thread = Thread(target = self.__listen, args = (self))
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


class NfcReader:

  def __init__(self, name, action):
    self.name = name
    self.action = action 
    self.start()

  def __react(self):
    if self.action is not None:
      self.action(self)

  def __start(self):
    thread = Thread(target = self.__listen, args = (self))
    thread.daemon = True
    thread.start()

  def __listen(self):
    def processTag(tag):
      logging.info( str(tag) + ' on ' + str(reader) )
      self.__react()
      return True
    while active:
      reader.connect(rdwr={'on-connect': processTag})

################################################################################
# METHODS
################################################################################

def init_boards():
  GPIO.setwarnings(False)
  GPIO.cleanup()
   
def led_on(led_pin):
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(led_pin, GPIO.OUT)
  GPIO.output(led_pin, 0)
  GPIO.output(led_pin, 1)

def led_off(led_pin):
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(led_pin, GPIO.OUT)
  GPIO.output(led_pin, 0)

def grove_buzzer_on(buzzer):
  Grove.digitalWrite(buzzer, 1)

def grove_buzzer_off(buzzer):
  Grove.digitalWrite(buzzer, 0)

def log_action(device):
  logging.info(str(device.name) + ' activated')

def accumulate_stats(button):
  stats[button.name]++

def action(on_functions, off_functions, timeout, button):
  try:
    for on_function in on_functions:
      on_function(button)
    sleep(timeout)
  finally:
    for off_function in off_functions:  
      off_function(button)

def nfc_readers(vendor_id, product_id):
  for device in usb.core.find(find_all=True):
    if device.idVendor == vendor_id and device.idProduct == product_id: 
      yield nfc.ContactlessFrontend('usb:' + str(device.bus).zfill(3) + ':' + str(device.address).zfill(3))

################################################################################
# MAIN
################################################################################

logging.info('Starting IOT service')

init_boards()

# idler = Idler(60000, action([], [], 1))

Button(16, 'RED', 
  action(
    on_functions = [ 
      # idler.reset_idle_time, 
      log_action, 
      accumulate_stats, 
      led_on(17), 
      grove_buzzer_on(6)
    ], 
    off_functions = [
      grove_buzzer_off(6), 
      led_off(17)
    ], 
    timeout = 0.1
  )
)

logging.info('Started')

def signal_handler(signal, frame):
  logging.info('Ctrl+C was detected!')
  active = False
  logging.info('Stopped')
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to exit')
signal.pause()

