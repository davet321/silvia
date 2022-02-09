#!/usr/bin/env python3

import RPi.GPIO as GPIO

print('WARNING!!! THIS WILL RUN HEATING ELEMENT AT 100% INDEFNITELY!!!')

GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)
pwm = GPIO.PWM(12, 20)
pwm.start(0)
try:
    while True:
        pwm.ChangeDutyCycle(1)
except KeyboardInterrupt:
    pass
finally:
    pwm.stop()
    GPIO.cleanup()
