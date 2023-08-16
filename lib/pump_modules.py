import serial
import time


PUMP_PORT = "/dev/ttyUSB1" #subject to change depending on the type of computer being used
BAUD_RATE = 9600
SERIAL_TIMEOUT = 2

class PumpKloehn:
    """
    This class defines specific implementation of the 
    commands for this pump
    """

    def __init__(self):
        """
        Initialize this object
        """
        self.syringe_pos = 0
        self._sleep_func = None
        self.serial_port = serial.Serial(PUMP_PORT, baudrate=BAUD_RATE, timeout=SERIAL_TIMEOUT)

    def set_sleep_func(self, sleep_func):
        """
        Apps like tkApp need to use special sleep functionality here
        Ignore otherwise
        """
        self._sleep_func = sleep_func

    def initialization(self):
        """
        Initialize the pump
        """
        self.write_cmd(self.serial_port, "W4R")

    def move_syringe(self, step_count, resolution):
        """
        Move the syringe to the given count
        (Is resolution relevant for non RPi/GPIO impl?)
        """
        pass

    def fill(self):
        """
        Fill the syringe
        """
        self.write_cmd(self.serial_port, "A40000R")
        pass

    def empty(self):
        """
        Empty the syringe
        """
        self.write_cmd(self.serial_port, "D40000R")
        pass
    
    def input_valve(self):
        """
        Move to input valve
        """
        self.write_cmd(self.serial_port, "IR")
        pass


    def output_valve(self):
        """
        Move to output valve
        """
        self.write_cmd(self.serial_port, "OR")
        pass

    def wash(self):
        """
        Wash the unit
        """
        self.fill()
        self.output_valve()
        self.empty()
        self.fill()
        self.output_valve()
        self.empty()
        self.fill()
        self.output_valve()
        self.empty()

    def sleep_msecs(self, t_msec):
        """
        Sleep for t_msec *milliseconds*
        We call this out explicitly in the method so that it is very obvious!
        lots of confusion if we mix secs and msecs
        We need to use this so that we can separate
        tkApp from console operations. Seems like tkApp doesn't like straight sleep calls
        """
        if self._sleep_func:
            self._sleep_func(t_msec)
        else:
            time.sleep(t_msec / 1000.0)
