
class pHInterface:
    """
    This class defines the high-level operations of the pH meter;
    specific implementation classes should be used for each device, with
    this class as the parent.
    """
    def __init__(self) -> None:
        self.serial_port_loc = None

    def get_measurement(self) -> dict:
        """Polls the meter for measurements of pH, emf, and temperature.

        ***Override this method in the child class***
        """
        raise NotImplementedError("Use derived pH meter implementation class!")
