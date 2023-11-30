# Write unit tests for ph_modules logic here
# Tests MUST start with `test_` for pytest to find them

import serial
import pytest
from unittest.mock import patch

from lib.services.ph import orion_star

def test_init_fails_without_serial() -> None:
    with pytest.raises(serial.SerialException):
        ph_meter = orion_star.OrionStarA215()

@patch.object(orion_star.OrionStarA215, '__init__')
def test_build_serial_command_A215(mock_init) -> None:
    mock_init.return_value = None
    ph_meter = orion_star.OrionStarA215()

    cmd = "GETMEAS"
    encoded_cmd = ph_meter.build_serial_command(cmd)
    assert isinstance(encoded_cmd, bytes)
    assert encoded_cmd == b"GETMEAS\r"

@patch.object(orion_star.OrionStarA215, '__init__')
def test_check_response_A215(mock_init) -> None:
    mock_init.return_value = None
    ph_meter = orion_star.OrionStarA215()

    dummy_res = "\n \n \nchannelname---SAMPLE,CH-1,pH,7.0,pH,0.0,mV,25.0,C"
    res_encoded = dummy_res.encode("ascii")

    res = ph_meter.check_response(res_encoded)
    assert isinstance(res, dict)
    assert res == {"pH": "7.0", "mV": "0.0", "temp": "25.0"}
