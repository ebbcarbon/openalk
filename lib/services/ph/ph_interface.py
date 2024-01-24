
class pHInterface:
    """
    This class defines the base interface to a pH probe.
    """
    def __init__(self) -> None:
        self.SERIAL_PORT_LOC = None

    def get_measurement(self) -> dict:
        raise NotImplementedError("Use derived pH implementation class!")
