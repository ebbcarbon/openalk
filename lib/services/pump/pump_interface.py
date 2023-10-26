import time


class PumpInterface:
    """
    This class defines an interface to a PumpModule.
    This class just defines the high-level operations of the pump,
    specific implementation classes should be used for devices.
    """

    def __init__(self):
        self.syringe_pos = None
        self.valve_state = None
        self._sleep_func = None

        # Conversion factor from mL to steps on the syringe
        self.ML_TO_STEPS_FACTOR = None

    def initialize_pump(self):
        """
        Send an initialize command to the pump.
        """
        pass

    def get_syringe_position(self):
        """
        Get the syringe's current position. Min/Max positions should
        be pre-defined in an Enum.
        """
        pass

    def set_syringe_position(self, pos):
        """
        Move the syringe to an absolute position. Min/Max positions should
        be pre-defined in an Enum.
        """
        pass

    def get_valve_state(self):
        """
        Get the current state of the pump's valve. Available states should
        be pre-defined in an Enum.
        """
        pass

    def set_valve_state(self, state):
        """
        Set the pump's valve to a specified state. Available states should
        be pre-defined in an Enum.
        """
        pass

    def fill(self):
        """
        Fill the syringe to the maximum position.
        """
        pass

    def empty(self):
        """
        Empty the syringe to the minimum position.
        """
        pass

    def wash(self):
        """
        Wash the unit.
        """
        pass

    def aspirate(self, steps, port):
        """
        Draw solution into syringe through the input port.
        """
        pass

    def dispense(self, steps, port):
        """
        Dispense solution from syringe through the output port.
        """
        pass

    def set_sleep_func(self, sleep_func):
        """
        Apps like tkApp need to use special sleep functionality here
        Ignore otherwise
        """
        self._sleep_func = sleep_func

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
