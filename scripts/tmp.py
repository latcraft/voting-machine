import usb
import nfc
import yaml

from piglow import PiGlow

################################################################################
# CONSTANTS
################################################################################

# NFC reader constants.
DEFAULT_VENDOR_ID  = 1254
DEFAULT_PRODUCT_ID = 21905

# PiDie constants.
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
PIDIE_BUTTON_NAMES  = ['RED',            'YELLOW',            'GREEN',            'BLUE']

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

# SparkFun constants
SF_RED_LED          = 17
SF_YELLOW_LED       = 27
SF_GREEN_LED        = 22
SF_LEDS             = [SF_RED_LED, SF_YELLOW_LED, SF_GREEN_LED]
SF_LED_OFF          = 0
SF_LED_ON           = 1
SF_RED_BUTTON       = 16
SF_YELLOW_BUTTON    = 20
SF_GREEN_BUTTON     = 21
SF_BUTTONS          = [SF_RED_BUTTON, SF_YELLOW_BUTTON, SF_GREEN_BUTTON]
SF_BUTTON_NAMES     = ['RED',         'YELLOW',         'GREEN'        ]




  if (config['board'] is not None):
    logging.info('Using board: ' + config['board'])
    if (config['board'] == 'piglow'):
      global piglow 
      piglow = PiGlow()  
      for led in PIGLOW_GROUPS:
        piglow.colour(led, PIGLOW_LED_OFF)      
    elif (config['board'] == 'pidie'):
      GPIO.setwarnings(False)
      GPIO.setmode(GPIO.BOARD)
      for led in PIDIE_LEDS:
        GPIO.setup(led, GPIO.OUT)
        GPIO.output(led, PIDIE_LED_OFF)
    elif (config['board'] == 'grove'):    
      Grove.pinMode(int(config['grove_led']), "OUTPUT")
      Grove.pinMode(int(config['grove_buzzer']), "OUTPUT")    
      print Grove.rtc_getTime()
    elif (config['board'] == 'sparkfun'):
      print Grove.rtc_getTime()
      Grove.pinMode(int(config['grove_buzzer']), "OUTPUT")
      GPIO.setwarnings(False)
      GPIO.setmode(GPIO.BCM)   
      for led in SF_LEDS:
        GPIO.setup(led, GPIO.OUT)
        GPIO.output(led, SF_LED_OFF)


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

def blinkSparkFunLed(color = 0, timeout = 1):
  GPIO.output(SF_LEDS[color], SF_LED_OFF)
  GPIO.output(SF_LEDS[color], SF_LED_ON)
  sleep(timeout)
  GPIO.output(SF_LEDS[color], SF_LED_OFF)

def beepGroveBuzzer(color = 0, timeout = 1):
  buzzer = int(config['grove_buzzer'])
  Grove.digitalWrite(buzzer, 1)
  sleep(timeout)
  Grove.digitalWrite(buzzer, 0)

def blinkSparkFunLedAndBeepGroveBuzzer(color = 0, timeout = 1):
  buzzer = int(config['grove_buzzer'])
  GPIO.output(SF_LEDS[color], SF_LED_OFF)
  GPIO.output(SF_LEDS[color], SF_LED_ON)
  Grove.digitalWrite(buzzer, 1)
  sleep(timeout)
  Grove.digitalWrite(buzzer, 0)
  GPIO.output(SF_LEDS[color], SF_LED_OFF)

def blinkGroveLedAndBeepGroveBuzzer(color = 0, timeout = 1):
  light = int(config['grove_led'])
  buzzer = int(config['grove_buzzer'])    
  Grove.digitalWrite(buzzer, 1)
  Grove.analogWrite(light, 255)
  sleep(timeout)
  Grove.digitalWrite(buzzer, 0)
  Grove.analogWrite(light, 0)


def nfc_readers(vendor_id, product_id):
  for device in usb.core.find(find_all=True):
    if device.idVendor == vendor_id and device.idProduct == product_id: 
      yield nfc.ContactlessFrontend('usb:' + str(device.bus).zfill(3) + ':' + str(device.address).zfill(3))



vendorId = int(config['nfc_vendor_id']) if config['nfc_vendor_id'] is not None else DEFAULT_VENDOR_ID  
productId = int(config['nfc_product_id']) if config['nfc_product_id'] is not None else DEFAULT_PRODUCT_ID
 
for idx, reader in enumerate(nfcReaders(vendorId, productId)):
  logging.info( str(idx + 1) + ': ' + str(reader) )
  thread = Thread(target = nfcReaderThread, args = (reader, actionFunction, idx, timeout))
  thread.daemon = True
  thread.start()


class NfcReader:

  def __init__(self, name, action):
    self.name = name
    self.action = action 
    self.start()

  def __react(self):
    if self.action is not None:
      self.action(self)

  def __start(self):
    thread = Thread(target = self.__listen)
    thread.daemon = True
    thread.start()

  def __listen(self):
    def processTag(tag):
      logging.info( str(tag) + ' on ' + str(reader) )
      self.__react()
      return True
    while active:
      reader.connect(rdwr={'on-connect': processTag})


config    = None

with open('/etc/device.yaml', 'r') as f:
  config = yaml.load(f)
