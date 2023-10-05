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
        self.steps_to_ml_factor = None
        self._sleep_func = None

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

    def fill_syringe(self):
        """
        Fill the syringe.
        """
        pass

    def empty_syringe(self):
        """
        Empty the syringe.
        """
        pass

    def wash_syringe(self):
        """
        Wash the unit.
        """
        pass

    def aspirate(self, steps, port):
        """
        Draw solution into syringe, specify number of steps and
        input port.
        """
        pass

    def dispense(self, steps, port):
        """
        Dispense solution from syringe, specify number of steps and
        output port.
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
