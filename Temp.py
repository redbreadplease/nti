import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT)
# GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

p = GPIO.PWM(26, 50)
p.start(0)

TURN_FRONT = 7
TURN_RIGHT = 2
TURN_LEFT = 11


def turn_left():
    p.ChangeDutyCycle(TURN_LEFT)
    time.sleep(1)


def turn_front():
    p.ChangeDutyCycle(TURN_FRONT)
    time.sleep(1)


def turn_right():
    p.ChangeDutyCycle(TURN_RIGHT)
    time.sleep(1)


try:
    while True:
        p.ChangeDutyCycle(int(input()))
        time.sleep(1)
    exit()
    for i in range(20):
        p.ChangeDutyCycle(i)
        time.sleep(1)
finally:
    p.stop()
    GPIO.cleanup()
