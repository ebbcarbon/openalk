# Write unit tests for pump modules here
# Tests MUST start with `test_` for pytest to find them

import pytest
from unittest.mock import Mock, patch

from lib.services.pump import norgren

# Important note on testing techniques:
# 
# These tests make generous use of the Mock() object within python's
# 'unittest' library to override certain attributes or return values
# during testing, in order to better simulate runtime behavior. For example,
# mocking the serial_port.read_until method allows injection of the
# expected serial response from a piece of hardware without needing to
# have the hardware present and operational, such that the testing of 
# the code is separated from the operation of the hardware.
# 
# For more information refer to the python documentation:
# https://docs.python.org/3/library/unittest.mock.html

SERIAL_REPR = "Serial<id=0xa81c10, open=True>(port='/dev/ttyUSB0', \
    baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=2, xonxoff=0,\
    rtscts=0)"

DUMMY_RES_POS = b'/0`48000'
DUMMY_RES_VALVE_STATE = b'/0`1'

EMPTY_RES = b''
BAD_HOST_RES = b'za%!/0axx3`4j*48000'
BAD_STATUS_RES = b'/0aaax1`zx%&48000'

@patch('serial.Serial', Mock(return_value=SERIAL_REPR))
def test_open_serial_port_success_norgren() -> None:
    """Test that the interface creates a serial port object properly
    when given a mocked successful return value from serial.Serial.
    """
    pump = norgren.VersaPumpV6()
    result = pump.open_serial_port()
    assert result == True

def test_open_serial_port_failure_norgren() -> None:
    """Test that the connection fails as expected if the port is
    not available (given a known bad port address).
    """
    pump = norgren.VersaPumpV6()
    pump.serial_port_loc = '/dev'
    result = pump.open_serial_port()
    assert result == False

def test_change_serial_port_from_default_norgren() -> None:
    """Test that the serial port address can be overridden as expected.
    """
    pump = norgren.VersaPumpV6()
    pump.open_serial_port(port='/dev/ttyUSB1')
    assert pump.serial_port_loc == '/dev/ttyUSB1'

def test_initialize_pump_norgren() -> None:
    """Test that the initialize_pump method returns the proper data object
    given a nominal response from the pump (DUMMY_RES_POS).
    """
    pump = norgren.VersaPumpV6()
    pump.serial_port = Mock()
    pump.serial_port.write = Mock(return_value=True)
    pump.serial_port.read_until = Mock(return_value=DUMMY_RES_POS)

    res = pump.initialize_pump()
    assert isinstance(res, dict)
    assert res == {"host_ready": True, "module_ready": True, "msg": "48000"}

def test_check_module_ready_norgren() -> None:
    """Test that the check_module_ready method returns the proper data object
    given a nominal response from the pump (DUMMY_RES_POS).
    """
    pump = norgren.VersaPumpV6()
    pump.serial_port = Mock()
    pump.serial_port.write = Mock(return_value=True)
    pump.serial_port.read_until = Mock(return_value=DUMMY_RES_POS)

    res = pump.check_module_ready()
    assert isinstance(res, bool)
    assert res == True

def test_check_volume_available_norgren() -> None:
    """Test the check_volume_available method works as expected in both
    the positive and negative case, accomplished by mocking the return
    of the get_syringe_position method.
    """
    pump = norgren.VersaPumpV6()

    pump.get_syringe_position = Mock(return_value=0)
    volume_available = pump.check_volume_available(volume=0.0025)
    assert volume_available == False

    pump.get_syringe_position = Mock(return_value=48000)
    volume_available = pump.check_volume_available(volume=0.0005)
    assert volume_available == True

def test_get_syringe_position_norgren() -> None:
    """Test that the get_syringe_position method returns the proper 
    data object given a nominal response from the pump (DUMMY_RES_POS).
    """
    pump = norgren.VersaPumpV6()
    pump.serial_port = Mock()
    pump.serial_port.write = Mock(return_value=True)
    pump.serial_port.read_until = Mock(return_value=DUMMY_RES_POS)

    res = pump.get_syringe_position()
    assert isinstance(res, int)
    assert res == 48000

def test_set_syringe_position_success_norgren() -> None:
    """Test that the set_syringe_position method returns the proper 
    data object given a nominal response from the pump (DUMMY_RES_POS).
    """
    pump = norgren.VersaPumpV6()
    pump.serial_port = Mock()
    pump.serial_port.write = Mock(return_value=True)
    pump.serial_port.read_until = Mock(return_value=DUMMY_RES_POS)

    res = pump.set_syringe_position(pos=48000)
    assert isinstance(res, dict)

def test_set_syringe_position_failure_norgren() -> None:
    """Test that the set_syringe_position method fails as expected given
    an invalid position value.
    """
    with pytest.raises(ValueError):
        pump = norgren.VersaPumpV6()
        res = pump.set_syringe_position(pos=50000)

def test_get_valve_state_norgren() -> None:
    """Test that the get_valve_state method returns the proper 
    data object given a nominal response from the pump 
    (DUMMY_RES_VALVE_STATE).
    """
    pump = norgren.VersaPumpV6()
    pump.serial_port = Mock()
    pump.serial_port.write = Mock(return_value=True)
    pump.serial_port.read_until = Mock(return_value=DUMMY_RES_VALVE_STATE)

    res = pump.get_valve_state()
    assert isinstance(res, norgren.ValveStates)
    assert res == norgren.ValveStates.INPUT

def test_set_valve_state_success_norgren() -> None:
    """Test that the set_valve_state method returns the proper 
    data object given a nominal response from the pump 
    (DUMMY_RES_VALVE_STATE).
    """
    pump = norgren.VersaPumpV6()
    pump.serial_port = Mock()
    pump.serial_port.write = Mock(return_value=True)
    pump.serial_port.read_until = Mock(return_value=DUMMY_RES_VALVE_STATE)

    res = pump.set_valve_state(state=norgren.ValveStates.INPUT)
    assert isinstance(res, dict)
    assert res == {"host_ready": True, "module_ready": True, "msg": "1"}

    res = pump.set_valve_state(state=norgren.ValveStates.BYPASS)
    assert isinstance(res, dict)
    assert res == {"host_ready": True, "module_ready": True, "msg": "1"}

    res = pump.set_valve_state(state=norgren.ValveStates.OUTPUT)
    assert isinstance(res, dict)
    assert res == {"host_ready": True, "module_ready": True, "msg": "1"}

def test_set_valve_state_failure_norgren() -> None:
    """Test that the set_valve_state method fails as expected given
    an invalid state value.
    """
    with pytest.raises(ValueError):
        pump = norgren.VersaPumpV6()
        res = pump.set_valve_state(state=1)

def test_fill_no_valve_change_norgren() -> None:
    """Test that the fill method returns the proper data object 
    given a nominal response from the pump (DUMMY_RES_POS), and that
    the method waits the proper amount of time for the pump to finish
    operating.
    """
    pump = norgren.VersaPumpV6()
    pump.serial_port = Mock()
    pump.serial_port.write = Mock(return_value=True)
    pump.serial_port.read_until = Mock(return_value=DUMMY_RES_POS)

    pump.get_valve_state = Mock(return_value=norgren.ValveStates.INPUT)
    pump.check_module_ready = Mock(side_effect=[False, True])

    res = pump.fill()
    assert isinstance(res, dict)
    assert res == {"host_ready": True, "module_ready": True, "msg": "48000"}

def test_fill_with_valve_change_norgren() -> None:
    """Test that the fill method returns the proper data object 
    given a nominal response from the pump (DUMMY_RES_POS), and that
    the method waits the proper amount of time for the pump to finish
    operating.
    """
    pump = norgren.VersaPumpV6()
    pump.serial_port = Mock()
    pump.serial_port.write = Mock(return_value=True)
    pump.serial_port.read_until = Mock(return_value=DUMMY_RES_POS)

    pump.get_valve_state = Mock(return_value=norgren.ValveStates.OUTPUT)
    pump.set_valve_state = Mock(return_value=True)
    pump.check_module_ready = Mock(side_effect=[False, True])

    res = pump.fill()
    assert isinstance(res, dict)
    assert res == {"host_ready": True, "module_ready": True, "msg": "48000"}

def test_empty_no_valve_change_norgren() -> None:
    """Test that the empty method returns the proper data object 
    given a nominal response from the pump (DUMMY_RES_POS), and that
    the method waits the proper amount of time for the pump to finish
    operating.
    """
    pump = norgren.VersaPumpV6()
    pump.serial_port = Mock()
    pump.serial_port.write = Mock(return_value=True)
    pump.serial_port.read_until = Mock(return_value=DUMMY_RES_POS)

    pump.get_valve_state = Mock(return_value=norgren.ValveStates.OUTPUT)
    pump.check_module_ready = Mock(side_effect=[False, True])

    res = pump.empty()
    assert isinstance(res, dict)
    assert res == {"host_ready": True, "module_ready": True, "msg": "48000"}

def test_empty_with_valve_change_norgren() -> None:
    """Test that the empty method returns the proper data object 
    given a nominal response from the pump (DUMMY_RES_POS), and that
    the method waits the proper amount of time for the pump to finish
    operating.
    """
    pump = norgren.VersaPumpV6()
    pump.serial_port = Mock()
    pump.serial_port.write = Mock(return_value=True)
    pump.serial_port.read_until = Mock(return_value=DUMMY_RES_POS)

    pump.get_valve_state = Mock(return_value=norgren.ValveStates.INPUT)
    pump.set_valve_state = Mock(return_value=True)
    pump.check_module_ready = Mock(side_effect=[False, True])

    res = pump.empty()
    assert isinstance(res, dict)
    assert res == {"host_ready": True, "module_ready": True, "msg": "48000"}

def test_wash_norgren() -> None:
    """Test that the wash method returns the proper data object 
    given a nominal response from the pump (DUMMY_RES_POS), and that
    the method waits the proper amount of time for the pump to finish
    operating.
    """
    pump = norgren.VersaPumpV6()
    pump.serial_port = Mock()
    pump.serial_port.write = Mock(return_value=True)
    pump.serial_port.read_until = Mock(return_value=DUMMY_RES_POS)

    pump.get_valve_state = Mock(return_value=norgren.ValveStates.INPUT)
    pump.set_valve_state = Mock(return_value=True)

    effect_list = [False, True] * pump.wash_cycles * 4
    pump.check_module_ready = Mock(side_effect=effect_list)

    res = pump.wash()
    assert isinstance(res, dict)
    assert res == {"host_ready": True, "module_ready": True, "msg": "48000"}

def test_liters_to_steps_norgren() -> None:
    """Test that the conversion from liters to steps on the pump's drive
    motor works as expected.
    """
    pump = norgren.VersaPumpV6()

    dummy_vol = 0.0025
    steps = pump.liters_to_steps(volume=dummy_vol)
    assert isinstance(steps, int)
    assert steps == (int(dummy_vol / pump.liters_per_step))

def test_aspirate_success_norgren() -> None:
    """Test that the aspirate method returns the proper data object 
    given a nominal response from the pump (DUMMY_RES_POS), and that
    the method waits the proper amount of time for the pump to finish
    operating.
    """
    pump = norgren.VersaPumpV6()
    pump.serial_port = Mock()
    pump.serial_port.write = Mock(return_value=True)
    pump.serial_port.read_until = Mock(return_value=DUMMY_RES_POS)

    pump.get_valve_state = Mock(return_value=norgren.ValveStates.OUTPUT)
    pump.set_valve_state = Mock(return_value=True)

    pump.check_module_ready = Mock(side_effect=[False, True])

    res = pump.aspirate(volume=0.0005)
    assert isinstance(res, dict)
    assert res == {"host_ready": True, "module_ready": True, "msg": "48000"}    

def test_aspirate_failure_norgren() -> None:
    """Test that the aspirate method fails as expected given
    an invalid volume.
    """
    with pytest.raises(ValueError):
        pump = norgren.VersaPumpV6()
        res = pump.aspirate(volume=0.5)

def test_dispense_success_norgren() -> None:
    """Test that the dispense method returns the proper data object 
    given a nominal response from the pump (DUMMY_RES_POS), and that
    the method waits the proper amount of time for the pump to finish
    operating.
    """
    pump = norgren.VersaPumpV6()
    pump.serial_port = Mock()
    pump.serial_port.write = Mock(return_value=True)
    pump.serial_port.read_until = Mock(return_value=DUMMY_RES_POS)

    pump.get_valve_state = Mock(return_value=norgren.ValveStates.INPUT)
    pump.set_valve_state = Mock(return_value=True)

    pump.check_module_ready = Mock(side_effect=[False, True])

    res = pump.dispense(volume=0.0005)
    assert isinstance(res, dict)
    assert res == {"host_ready": True, "module_ready": True, "msg": "48000"}    

def test_dispense_failure_norgren() -> None:
    """Test that the dispense method fails as expected given
    an invalid volume.
    """
    with pytest.raises(ValueError):
        pump = norgren.VersaPumpV6()
        res = pump.dispense(volume=0.5)

def test_build_serial_command_norgren() -> None:
    """Test proper formatting of serial commands to meet the pump's
    specifications.
    """
    pump = norgren.VersaPumpV6()

    cmd = "W4R"
    encoded_cmd = pump._build_serial_command(cmd)
    assert isinstance(encoded_cmd, bytes)
    assert encoded_cmd == b"/1W4R\r"

def test_send_pump_command_norgren() -> None:
    """Test that the example response (DUMMY_RES_POS) flows through the
    processing chain properly when _send_pump_command is called.
    """
    pump = norgren.VersaPumpV6()
    pump.serial_port = Mock()
    pump.serial_port.write = Mock(return_value=True)
    pump.serial_port.read_until = Mock(return_value=DUMMY_RES_POS)

    cmd = "?"
    res = pump._send_pump_command(cmd)
    assert isinstance(res, dict)
    assert res == {"host_ready": True, "module_ready": True, "msg": "48000"}

def test_check_response_success_norgren() -> None:
    """Test that the example response (DUMMY_RES_POS) is processed/parsed
    successfully and returns the expected data object.
    """
    pump = norgren.VersaPumpV6()

    res = pump._check_response(DUMMY_RES_POS)
    assert isinstance(res, dict)
    assert res == {"host_ready": True, "module_ready": True, "msg": "48000"}

def test_check_response_failure_empty_norgren() -> None:
    """Test that a null serial response (EMPTY_RES) causes a failure
    in the expected manner.
    """
    with pytest.raises(ValueError):
        pump = norgren.VersaPumpV6()
        res = pump._check_response(EMPTY_RES)

def test_check_response_failure_badhost_norgren() -> None:
    """Test that an invalid serial response (BAD_HOST_RES) causes a failure
    in the expected manner.
    """
    with pytest.raises(ValueError):
        pump = norgren.VersaPumpV6()
        res = pump._check_response(BAD_HOST_RES)

def test_check_response_failure_badstatus_norgren() -> None:
    """Test that an invalid serial response (BAD_STATUS_RES) causes a failure
    in the expected manner.
    """
    with pytest.raises(ValueError):
        pump = norgren.VersaPumpV6()
        res = pump._check_response(BAD_STATUS_RES)
