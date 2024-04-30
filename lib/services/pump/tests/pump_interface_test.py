import pytest

from lib.services.pump.norgren import ValveStates
from lib.services.pump.pump_interface import PumpInterface

def test_init_base_interface() -> None:
    """Test to make sure the base class initializes successfully and has
    the expected attributes.
    """
    interface = PumpInterface()
    assert hasattr(interface, 'serial_port_loc')
    assert hasattr(interface, 'wash_cycles')
    assert hasattr(interface, 'liters_per_step')

def test_initialize_pump_not_implemented() -> None:
    """Test to make sure the initialize_pump method fails if not 
    overridden by a subclass.
    """
    interface = PumpInterface()
    with pytest.raises(NotImplementedError):
        interface.initialize_pump()

def test_get_syringe_position_not_implemented() -> None:
    """Test to make sure the get_syringe_position method fails if not 
    overridden by a subclass.
    """
    interface = PumpInterface()
    with pytest.raises(NotImplementedError):
        interface.get_syringe_position()

def test_set_syringe_position_not_implemented() -> None:
    """Test to make sure the set_syringe_position method fails if not 
    overridden by a subclass.
    """
    interface = PumpInterface()
    with pytest.raises(NotImplementedError):
        interface.set_syringe_position(pos=48000)

def test_get_valve_state_not_implemented() -> None:
    """Test to make sure the get_valve_state method fails if not 
    overridden by a subclass.
    """
    interface = PumpInterface()
    with pytest.raises(NotImplementedError):
        interface.get_valve_state()

def test_set_valve_state_not_implemented() -> None:
    """Test to make sure the set_valve_state method fails if not 
    overridden by a subclass.
    """
    interface = PumpInterface()
    with pytest.raises(NotImplementedError):
        interface.set_valve_state(state=ValveStates.INPUT)

def test_fill_not_implemented() -> None:
    """Test to make sure the fill method fails if not 
    overridden by a subclass.
    """
    interface = PumpInterface()
    with pytest.raises(NotImplementedError):
        interface.fill()

def test_empty_not_implemented() -> None:
    """Test to make sure the empty method fails if not 
    overridden by a subclass.
    """
    interface = PumpInterface()
    with pytest.raises(NotImplementedError):
        interface.empty()

def test_wash_not_implemented() -> None:
    """Test to make sure the wash method fails if not 
    overridden by a subclass.
    """
    interface = PumpInterface()
    with pytest.raises(NotImplementedError):
        interface.wash()

def test_liters_to_steps_not_implemented() -> None:
    """Test to make sure the liters_to_steps method fails if not 
    overridden by a subclass.
    """
    interface = PumpInterface()
    with pytest.raises(NotImplementedError):
        interface.liters_to_steps(volume=0.0015)

def test_aspirate_not_implemented() -> None:
    """Test to make sure the aspirate method fails if not 
    overridden by a subclass.
    """
    interface = PumpInterface()
    with pytest.raises(NotImplementedError):
        interface.aspirate(volume=0.0015)

def test_dispense_not_implemented() -> None:
    """Test to make sure the dispense method fails if not 
    overridden by a subclass.
    """
    interface = PumpInterface()
    with pytest.raises(NotImplementedError):
        interface.dispense(volume=0.0015)
