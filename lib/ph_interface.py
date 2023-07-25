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


def readpH(s):

    s.reset_input_buffer()

    serialString = ""
    while 1:
        if s.in_waiting > 0:
            serialString = s.readline()
            try:
                serialString = serialString.decode("Ascii")
                arr = serialString.split(",")
                if serialString.find("\rA211 pH") != -1:
                    i = arr.index(" mV")
                    emf = arr[i - 1]
                    pH = arr[i - 3]
                    return emf, pH
            except:
                pass
