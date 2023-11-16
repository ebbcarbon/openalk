
class pHInterface:
    """
    This class defines an interface to a pH probe.
    """
    def __init__(self):
        self.SERIAL_PORT_LOC = None

    def get_measurement(self):
        raise NotImplementedError("Use derived pH implementation class!")
