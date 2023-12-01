import serial
import pytest
from unittest.mock import patch

from lib.services.pump import norgren

def test_init_fails_without_serial() -> None:
    with pytest.raises(serial.SerialException):
        pump = norgren.VersaPumpV6()

@patch.object(norgren.VersaPumpV6, '__init__')
def test_build_serial_command_norgren(mock_init) -> None:
    mock_init.return_value = None
    pump = norgren.VersaPumpV6()

    cmd = "W4R"
    encoded_cmd = pump._build_serial_command(cmd)
    assert isinstance(encoded_cmd, bytes)
    assert encoded_cmd == b"/1W4R\r"

@patch.object(norgren.VersaPumpV6, "get_syringe_position")
@patch.object(norgren.VersaPumpV6, "__init__")
def test_check_volume_available_norgren(mock_init,
                                      mock_get_syringe_position) -> None:
    mock_init.return_value = None
    pump = norgren.VersaPumpV6()
    pump.LITERS_PER_STEP = 0.00000005

    mock_get_syringe_position.return_value = 0
    volume_available = pump.check_volume_available(volume=0.0025)
    assert volume_available == False

    mock_get_syringe_position.return_value = 48000
    volume_available = pump.check_volume_available(volume=0.0005)
    assert volume_available == True

@patch.object(norgren.VersaPumpV6, '__init__')
def test_liters_to_steps_norgren(mock_init) -> None:
    mock_init.return_value = None
    pump = norgren.VersaPumpV6()
    pump.LITERS_PER_STEP = 0.00000005

    dummy_vol = 0.0025
    steps = pump.liters_to_steps(volume=dummy_vol)
    assert isinstance(steps, int)
    assert steps == (int(dummy_vol / pump.LITERS_PER_STEP))

@patch.object(norgren.VersaPumpV6, '__init__')
def test_check_response_norgren(mock_init) -> None:
    mock_init.return_value = None
    pump = norgren.VersaPumpV6()

    dummy_res = "/0`48000"
    res_encoded = dummy_res.encode("ascii")

    res = pump._check_response(res_encoded)
    assert isinstance(res, dict)
    assert res == {"host_ready": True, "module_ready": True, "msg": "48000"}
