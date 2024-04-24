
import pytest

from lib.services.ph.ph_interface import pHInterface

def test_init_base_interface() -> None:
    """Test to make sure the base class instantiates successfully and has
    the expected attributes.
    """
    interface = pHInterface()
    assert hasattr(interface, 'serial_port_loc')

def test_get_measurement_not_implemented() -> None:
    """Test to make sure the get_measurement method fails if not
    overridden by a subclass.
    """
    interface = pHInterface()
    with pytest.raises(NotImplementedError):
        interface.get_measurement()
