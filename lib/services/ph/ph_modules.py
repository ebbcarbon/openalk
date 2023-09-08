import random
import time

import serial

from lib.services.ph.ph_interface import pHInterface


BAUDRATE = 9600
SERIAL_TIMEOUT_S = 2
BYTESIZE = 8


class pH_meter_A211(pHInterface):
    """
    A211 probe
    """

    def __init__(self, serial_path):
        """
        Initialize this object
        """
        super().__init__()

        self.serial = serial.Serial(
            serial_path, baudrate=BAUDRATE, bytesize=BYTESIZE, timeout=SERIAL_TIMEOUT_S
        )

        self._device_functional = True

    def read_emf_pH(self):
        """
        Read the emf and pH
        """
        self.serial.reset_input_buffer()

        serial_string = ""
        while True:
            if self.serial.in_waiting > 0:
                serial_string = self.serial.readline()
                try:
                    serial_string = serial_string.decode("Ascii")
                    arr = serial_string.split(",")
                    if serial_string.find("\rA211 pH") != -1:
                        i = arr.index(" mV")
                        emf = arr[i - 1]
                        pH = arr[i - 3]
                        return emf, pH
                except:
                    pass


class pH_meter_A215(pHInterface):
    """
    A215 probe
    """

    def __init__(self, serial_path):
        """
        Initialize this object
        """
        super().__init__()

        self.serial = serial.Serial(
            serial_path, baudrate=BAUDRATE, bytesize=BYTESIZE, timeout=SERIAL_TIMEOUT_S
        )

        self._device_functional = True

    def read_emf_pH(self):
        """
        Read the emf and pH
        """
        self.serial.reset_input_buffer()

        serial_string = ""
        while True:
            if self.serial.in_waiting > 0:
                serial_string = self.serial.readline()
                try:
                    serial_string = serial_string.decode("Ascii")
                    arr = serial_string.split(",")
                    # TODO: THIS CODE WON'T WORK FOR THIS MODULE
                    if serial_string.find("\rA215") != -1:
                        i = arr.index(" mV")
                        emf = arr[i - 1]
                        pH = arr[i - 3]
                        return emf, pH
                except:
                    pass


class pH_meter_simulated(pHInterface):
    """
    simulated in case you don't have hardware
    """

    def __init__(self):
        super().__init__()

        random.seed(time.time())

        self._device_functional = True

    def read_emf_pH(self):

        emf = random.uniform(0.1, 1.0)
        pH = random.uniform(3.5, 4.2)
        return emf, pH
