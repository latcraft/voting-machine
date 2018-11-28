#!/usr/bin/python

import sys
import signal
import logging
import time
import inspect
import collections
import firebase_admin
import fcntl, socket, struct

from firebase_admin import credentials
from firebase_admin import db

from multiprocessing import Queue
from threading import Thread, Lock
from time import sleep

################################################################################
# LOGGING
################################################################################

logging.basicConfig(
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

class Sender:

  def __init__(self, name, queue, db):
    self.name = name
    self.queue = queue
    self.db = db
    self.__start()

  def __start(self):
    thread = Thread(target = self.__listen)
    thread.daemon = True
    thread.start()

  def __listen(self):
    while True:       
      item = queue.get()
      try:
        self.__send(item)
      except:
        print "Unexpected error:", sys.exc_info()[0]

  def __send(self, item):
    response = db.push().set({
      'device': self.name,
      'color': item[0].lower(),
      'created': item[1]
    })


################################################################################
# METHODS
################################################################################
  
def getHwAddr(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return ':'.join(['%02x' % ord(char) for char in info[18:24]])

################################################################################
# MAIN
################################################################################

logging.info('Starting IOT service')

firebase_admin.initialize_app(credentials.Certificate('firebase.json'), {
  'databaseURL': 'https://devternity-voting.firebaseio.com'
})

queue = Queue()
db = db.reference('votes')
sender = Sender(getHwAddr('enp0s3'), queue, db)

queue.put(('RED', time.mktime(time.gmtime()))) 

logging.info('Started')

def signal_handler(signal, frame):
  logging.info('Ctrl+C was detected!')
  active = False
  logging.info('Stopped')
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to exit')
signal.pause()

