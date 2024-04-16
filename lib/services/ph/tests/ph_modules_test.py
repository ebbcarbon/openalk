# Write unit tests for ph modules here
# Tests MUST start with `test_` for pytest to find them

import pytest
from unittest.mock import patch, Mock

from lib.services.ph import orion_star

SERIAL_REPR = "Serial<id=0xa81c10, open=True>(port='/dev/ttyACM0', \
    baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=600, xonxoff=0,\
    rtscts=0)"

DUMMY_RES = b'GETMEAS         \r\n\r\n\rA215 pH,X51250,3.04,ABCDE,12/07/23\
    09:30:40,---,CH-1,pH,4.61,pH,111.2, mV,25.0,C,89.1,%,M100,#1\n\r\r>'

EMPTY_RES = b'GETMEAS         \r\n\r\n\r>'

@patch('serial.Serial', Mock(return_value=SERIAL_REPR))
def test_open_serial_port_success_A215() -> None:
    ph_meter = orion_star.OrionStarA215()
    result = ph_meter.open_serial_port()
    assert result == True

def test_open_serial_port_failure_A215() -> None:
    ph_meter = orion_star.OrionStarA215()
    result = ph_meter.open_serial_port()
    assert result == False

def test_change_serial_port_from_default_A215() -> None:
    ph_meter = orion_star.OrionStarA215()
    ph_meter.open_serial_port(port='/dev/ttyACM1')
    assert ph_meter.serial_port_loc == '/dev/ttyACM1'

def test_get_measurement_A215() -> None:
    ph_meter = orion_star.OrionStarA215()
    ph_meter.serial_port = Mock()
    ph_meter.serial_port.write = Mock(return_value=True)
    ph_meter.serial_port.read_until = Mock(return_value=DUMMY_RES)

    res = ph_meter.get_measurement()
    assert isinstance(res, dict)
    assert res == {"pH": "4.61", "mV": "111.2", "temp": "25.0"}

def test_build_serial_command_A215() -> None:
    ph_meter = orion_star.OrionStarA215()

    cmd = "GETMEAS"
    encoded_cmd = ph_meter._build_serial_command(cmd)
    assert isinstance(encoded_cmd, bytes)
    assert encoded_cmd == b"GETMEAS\r"

def test_send_meter_command_A215() -> None:
    ph_meter = orion_star.OrionStarA215()
    ph_meter.serial_port = Mock()
    ph_meter.serial_port.write = Mock(return_value=True)
    ph_meter.serial_port.read_until = Mock(return_value=DUMMY_RES)

    cmd = "GETMEAS"
    res = ph_meter._send_meter_command(cmd)
    assert isinstance(res, dict)
    assert res == {"pH": "4.61", "mV": "111.2", "temp": "25.0"}

def test_check_response_success_A215() -> None:
    ph_meter = orion_star.OrionStarA215()

    res = ph_meter._check_response(DUMMY_RES)
    assert isinstance(res, dict)
    assert res == {"pH": "4.61", "mV": "111.2", "temp": "25.0"}

def test_check_response_failure_A215() -> None:
    with pytest.raises(IndexError):
        ph_meter = orion_star.OrionStarA215()
        res = ph_meter._check_response(EMPTY_RES)