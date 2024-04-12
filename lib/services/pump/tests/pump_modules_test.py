# Write unit tests for pump modules here
# Tests MUST start with `test_` for pytest to find them

import pytest
from unittest.mock import patch, Mock

from lib.services.pump import norgren

SERIAL_REPR = "Serial<id=0xa81c10, open=True>(port='/dev/ttyUSB0', \
    baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=2, xonxoff=0,\
    rtscts=0)"

@patch('serial.Serial', Mock(return_value=SERIAL_REPR))
def test_open_serial_port_success_norgren() -> None:
    pump = norgren.VersaPumpV6()
    result = pump.open_serial_port()
    assert result == True

def test_open_serial_port_failure_norgren() -> None:
    pump = norgren.VersaPumpV6()
    result = pump.open_serial_port()
    assert result == False

def test_change_serial_port_from_default_norgren() -> None:
    pump = norgren.VersaPumpV6()
    pump.open_serial_port(port='/dev/ttyUSB1')
    assert pump.serial_port_loc == '/dev/ttyUSB1'

def test_build_serial_command_norgren() -> None:
    pump = norgren.VersaPumpV6()

    cmd = "W4R"
    encoded_cmd = pump._build_serial_command(cmd)
    assert isinstance(encoded_cmd, bytes)
    assert encoded_cmd == b"/1W4R\r"

def test_check_volume_available_norgren() -> None:
    pump = norgren.VersaPumpV6()

    pump.get_syringe_position = Mock(return_value=0)
    volume_available = pump.check_volume_available(volume=0.0025)
    assert volume_available == False

    pump.get_syringe_position = Mock(return_value=48000)
    volume_available = pump.check_volume_available(volume=0.0005)
    assert volume_available == True

def test_liters_to_steps_norgren() -> None:
    pump = norgren.VersaPumpV6()

    dummy_vol = 0.0025
    steps = pump.liters_to_steps(volume=dummy_vol)
    assert isinstance(steps, int)
    assert steps == (int(dummy_vol / pump.liters_per_step))

def test_check_response_norgren() -> None:
    pump = norgren.VersaPumpV6()

    dummy_res = "/0`48000"
    res_encoded = dummy_res.encode("ascii")

    res = pump._check_response(res_encoded)
    assert isinstance(res, dict)
    assert res == {"host_ready": True, "module_ready": True, "msg": "48000"}
