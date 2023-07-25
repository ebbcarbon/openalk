import RPi.GPIO as GPIO


class Pins:
    def __init__(self):

        GPIO.setwarnings(False)

        self.DIR = 20
        self.STEP = 21
        self.MODE = (14, 15, 18)
        self.CHANGE = 3

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.DIR, GPIO.OUT)
        GPIO.setup(self.STEP, GPIO.OUT)
        GPIO.setup(self.MODE, GPIO.OUT)
        GPIO.setup(self.CHANGE, GPIO.OUT)
