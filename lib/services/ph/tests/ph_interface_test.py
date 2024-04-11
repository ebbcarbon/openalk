
import pytest

from lib.services.ph.ph_interface import pHInterface

def test_init_base_interface() -> None:
    interface = pHInterface()
    assert hasattr(interface, 'serial_port_loc')

def test_get_measurement_not_implemented() -> None:
    interface = pHInterface()
    with pytest.raises(NotImplementedError):
        interface.get_measurement()
