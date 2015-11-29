#!/usr/bin/python

import time
import grovepi

button1 = 2
button2 = 3
button3 = 4
light   = 5
buzzer  = 6

pressed = False

grovepi.pinMode(button1, "INPUT")
grovepi.pinMode(button2, "INPUT")
grovepi.pinMode(button3, "INPUT")
grovepi.pinMode(light,   "OUTPUT")
grovepi.pinMode(buzzer,  "OUTPUT")

try:
  while 1:
    grovepi.analogWrite(light, 0 if int(time.time() * 1000) // 250 % 2 else 255)
    if not pressed and grovepi.digitalRead(button1) == 1:
      f = open('app.1.stat', 'a'); f.write('1'); f.close()
      grovepi.digitalWrite(buzzer, 1); pressed = True
    if not pressed and grovepi.digitalRead(button2) == 1:
      f = open('app.2.stat', 'a'); f.write('1'); f.close()
      grovepi.digitalWrite(buzzer, 1); pressed = True
    if not pressed and grovepi.digitalRead(button3) == 1:
      f = open('app.3.stat', 'a'); f.write('1'); f.close()
      grovepi.digitalWrite(buzzer, 1); pressed = True
    if (pressed and
        grovepi.digitalRead(button1) == 0 and
        grovepi.digitalRead(button2) == 0 and
        grovepi.digitalRead(button3) == 0):
      grovepi.digitalWrite(buzzer, 0); pressed = False
except:
  grovepi.digitalWrite(buzzer, 0)
  grovepi.analogWrite(light, 255)
