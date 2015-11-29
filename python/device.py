#!/usr/bin/python

# TODO 0. read configuration data? device mapping?
# TODO 3. save data to temporary db (sqllite?)
# TODO 4. poll database for new records
# TODO 5. send data to remote server (HTTP(S) POST?)

import sys
import signal
import usb
import nfc
import yaml
import logging
import RPi.GPIO as GPIO

from piglow import PiGlow
from threading import Thread
from time import sleep

# Logging setup
logging.basicConfig(
  filename = '/var/log/voter.log', 
  level    = logging.DEBUG, 
  format   = '%(asctime)s %(message)s', 
  datefmt  = '%Y-%m-%d %H:%M:%S'
)

# NFC reader constants
DEFAULT_VENDOR_ID  = 1254
DEFAULT_PRODUCT_ID = 21905

# PiDie constants
PIDIE_RED_LED1      = 7
PIDIE_RED_LED2      = 11
PIDIE_GREEN_LED1    = 12
PIDIE_GREEN_LED2    = 13
PIDIE_YELLOW_LED1   = 15
PIDIE_YELLOW_LED2   = 16
PIDIE_BLUE_LED1     = 18
PIDIE_BLUE_LED2     = 22
PIDIE_WHITE_LED1    = 8
PIDIE_LEDS          = [PIDIE_RED_LED1, PIDIE_YELLOW_LED1, PIDIE_GREEN_LED1, PIDIE_BLUE_LED1, PIDIE_RED_LED2, PIDIE_GREEN_LED2, PIDIE_YELLOW_LED2, PIDIE_BLUE_LED2, PIDIE_WHITE_LED1]
PIDIE_LED_OFF       = 1
PIDIE_LED_ON        = 0
PIDIE_RED_BUTTON    = 21
PIDIE_GREEN_BUTTON  = 19
PIDIE_YELLOW_BUTTON = 24
PIDIE_BLUE_BUTTON   = 26
PIDIE_BUTTONS       = [PIDIE_RED_BUTTON, PIDIE_YELLOW_BUTTON, PIDIE_GREEN_BUTTON, PIDIE_BLUE_BUTTON]

# PiGlow constants
piglow              = None
PIGLOW_WHITE_GROUP  = 1
PIGLOW_BLUE_GROUP   = 2
PIGLOW_GREEN_GROUP  = 3
PIGLOW_YELLOW_GROUP = 4
PIGLOW_ORANGE_GROUP = 5
PIGLOW_RED_GROUP    = 6
PIGLOW_GROUPS       = [PIGLOW_RED_GROUP, PIGLOW_YELLOW_GROUP, PIGLOW_GREEN_GROUP, PIGLOW_BLUE_GROUP, PIGLOW_WHITE_GROUP, PIGLOW_ORANGE_GROUP]
PIGLOW_LED_OFF      = 0
PIGLOW_LED_ON       = 255

# Methods

active = True

def readConfig():
  with open('/etc/voter.yaml', 'r') as f:
    config = yaml.load(f)
  return config

def initLeds(config):
  if (config['led_device'] == 'piglow'):
    global piglow 
    piglow = PiGlow()  
    for led in PIGLOW_GROUPS:
      piglow.colour(led, PIGLOW_LED_OFF)      
  elif (config['led_device'] == 'pidie'):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    for led in PIDIE_LEDS:
      GPIO.setup(led, GPIO.OUT)
      GPIO.output(led, PIDIE_LED_OFF)
   
def nfcReaders(vendorId, productId):
  for device in usb.core.find(find_all=True):
    if device.idVendor == vendorId and device.idProduct == productId: 
      yield nfc.ContactlessFrontend('usb:' + str(device.bus).zfill(3) + ':' + str(device.address).zfill(3))

def blinkPiGlowLed(color = 0, timeout = 1):
  piglow.colour(PIGLOW_GROUPS[color], PIGLOW_LED_OFF)
  piglow.colour(PIGLOW_GROUPS[color], PIGLOW_LED_ON)
  sleep(timeout)
  piglow.colour(PIGLOW_GROUPS[color], PIGLOW_LED_OFF)
   
def blinkPiDieLed(color = 0, timeout = 1):
  GPIO.output(PIDIE_LEDS[color], PIDIE_LED_OFF)
  GPIO.output(PIDIE_LEDS[color], PIDIE_LED_ON)
  sleep(timeout)
  GPIO.output(PIDIE_LEDS[color], PIDIE_LED_OFF)   

def buttonReaderThread(button, ledFunction, timeout):
  GPIO.setup(PIDIE_BUTTONS[button], GPIO.IN, pull_up_down = GPIO.PUD_UP)
  prev_input = GPIO.input(PIDIE_BUTTONS[button])
  while active:
    input = GPIO.input(PIDIE_BUTTONS[button])
    if ((not prev_input) and input):
      logging.info(str(PIDIE_BUTTONS[button]) + ' pressed')
      if ledFunction is not None:
        ledFunction(button, timeout)
    prev_input = input
    sleep(0.05)    

def nfcReaderThread(reader, ledFunction, color, timeout):
  def processTag(tag):
    logging.info( str(tag) + ' on ' + str(reader) )
    if ledFunction is not None:
      ledFunction(color, timeout)
    return True
  while active:
    reader.connect(rdwr={'on-connect': processTag})

# Main

logging.info('Starting voter service')

config = readConfig()
initLeds(config)

timeout = 0.3
ledFunction = None
if (config['led_device'] == 'pidie'):
  ledFunction = blinkPiDieLed
elif (config['led_device'] == 'piglow'):
  ledFunction = blinkPiGlowLed

if (config['led_device'] == 'pidie'):
  for idx, button in enumerate(PIDIE_BUTTONS):
    thread = Thread(target = buttonReaderThread, args = (idx, ledFunction, timeout))
    thread.daemon = True
    thread.start()

for idx, reader in enumerate(nfcReaders(DEFAULT_VENDOR_ID, DEFAULT_PRODUCT_ID)):
  logging.info( str(idx + 1) + ': ' + str(reader) )
  thread = Thread(target = nfcReaderThread, args = (reader, ledFunction, idx, timeout))
  thread.daemon = True
  thread.start()

logging.info('Started')

def signal_handler(signal, frame):
  logging.info('Ctrl+C was detected!')
  active = False
  logging.info('Stopped')
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to exit')
signal.pause()











