import time


class PumpInterface:
    """
    This class defines an interface to a PumpModule
    This class just defines the high-level operations of the pump
    Specific implementation classes should be used for devices
    """

    def __init__(self):
        """
        Initialize this object
        """
        self.syringe_pos = 0
        self._sleep_func = None

    def set_sleep_func(self, sleep_func):
        """
        Apps like tkApp need to use special sleep functionality here
        Ignore otherwise
        """
        self._sleep_func = sleep_func

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
