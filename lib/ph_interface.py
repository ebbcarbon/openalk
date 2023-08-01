class pHInterface:
    """
    This class defines an interface to a pH probe interface
    """

    def __init__(self):
        """
        Initialize this object
        """
        self._device_functional = False

    def device_functional(self):
        """
        Is the device working
        """
        return self._device_functional

    def read_emf_pH(self):
        """ """
        raise NotImplementedError("Use derived pH implementation class!")
