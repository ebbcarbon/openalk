
class PumpInterface:
    """
    This class defines the high-level operations of the pump;
    specific implementation classes should be used for each device, with
    this class as the parent.
    """
    def __init__(self):
        self.serial_port_loc = None
        self.wash_cycles = None
        self.liters_per_step = None

    def initialize_pump(self):
        """Send an initialize command to the pump.
        """
        raise NotImplementedError("Use derived pump implementation class!")

    def get_syringe_position(self):
        """Get the syringe's current position. Min/Max positions should
        be pre-defined in an Enum.
        """
        raise NotImplementedError("Use derived pump implementation class!")

    def set_syringe_position(self, pos):
        """Move the syringe to an absolute position. Min/Max positions should
        be pre-defined in an Enum.
        """
        raise NotImplementedError("Use derived pump implementation class!")

    def get_valve_state(self):
        """Get the current state of the pump's valve. Available states should
        be pre-defined in an Enum.
        """
        raise NotImplementedError("Use derived pump implementation class!")

    def set_valve_state(self, state):
        """Set the pump's valve to a specified state. Available states should
        be pre-defined in an Enum.
        """
        raise NotImplementedError("Use derived pump implementation class!")

    def fill(self):
        """Fill the syringe to the maximum position.
        """
        raise NotImplementedError("Use derived pump implementation class!")

    def empty(self):
        """Empty the syringe to the minimum position.
        """
        raise NotImplementedError("Use derived pump implementation class!")

    def wash(self):
        """Wash the unit.
        """
        raise NotImplementedError("Use derived pump implementation class!")

    def liters_to_steps(self, volume):
        """Translates volume in liters to steps on the syringe.
        """
        raise NotImplementedError("Use derived pump implementation class!")

    def aspirate(self, volume):
        """Draw solution into syringe through the input port.
        """
        raise NotImplementedError("Use derived pump implementation class!")

    def dispense(self, volume):
        """Dispense solution from syringe through the output port.
        """
        raise NotImplementedError("Use derived pump implementation class!")
