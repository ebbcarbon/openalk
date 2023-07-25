import time


class PumpInterface:
    """
    This class defines an interface to a PumpModule
    This class just defines the high-level operations of the pump
    Specific implementation classes should be used for devices
    """
    def __init__(self):
        self._sleep_func = None

    def set_sleep_func(self, sleep_func):
        """
        Apps like tkApp need to use special sleep functionality here
        """
        self._sleep_func = sleep_func

    def MoveSyringe(self, step_count, pins, resolution):
        """
        Move the syringe to the given count
        """
        pass

    def fill(self):
        """
        Fill the syringe
        """
        pass

    def empty(self):
        """
        Empty the syringe
        """
        pass

    def wash(self):
        """
        Wash the unit
        """
        self.fill()
        self.empty()
        self.fill()
        self.empty()
        self.fill()
        self.empty()

    def sleep(self, t_msec):
        """
        Sleep for t_msec milliseconds
        We need to use this so that we can separate
        tkApp from console operations. Seems like tkApp doesn't like straight sleep calls
        """
        if self._sleep_func:
            self._sleep_func(t_msec)
        else:
            time.sleep(t_msec/1000.0)
