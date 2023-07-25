import time

import RPi.GPIO as GPIO

from .pump_interface import PumpInterface
from . import rpi_pin_setup

RESOLUTION = {
            "Full": (0, 0, 0),
            "Half": (1, 0, 0),
            "1/4": (0, 1, 0),
            "1/8": (1, 1, 0),
            "1/16": (0, 0, 1),
            "1/32": (1, 0, 1),
        }

class PumpRpi(PumpInterface):
    """
    This class defines an interface to a PumpModule
    This class just defines the high-level operations of the pump
    Specific implementation classes should be used for devices
    """
    def __init__(self):
        super().__init__()

        self.pins = rpi_pin_setup.Pins()

    def move_syringe(self, step_count, resolution):
        """
        Move the syringe to the given count
        """
        GPIO.output(self.pins.CHANGE, GPIO.LOW)

        if step_count > 0:
            direction = 1
        else:
            direction = 0

        self.syringe_pos = self.syringe_pos + step_count

        step_count = abs(step_count)

        GPIO.output(self.pins.MODE, RESOLUTION[resolution])

        GPIO.output(self.pins.DIR, direction)
        for x in range(step_count):
            GPIO.output(self.pins.STEP, GPIO.HIGH)
            self.sleep_msecs(1)
            GPIO.output(self.pins.STEP, GPIO.LOW)
            self.sleep_msecs(1)

    def fill(self):
        """
        Fill the syringe
        """
        GPIO.output(self.pins.CHANGE, GPIO.HIGH)
        self.move_syringe(7000 - int(self.syringe_pos / 4), "Full")

    def empty(self):
        """
        Empty the syringe
        """
        GPIO.output(self.pins.CHANGE, GPIO.LOW)
        self.move_syringe(-1 * self.syringe_pos, "Full")
