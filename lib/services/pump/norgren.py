import time
import serial
import logging
from enum import Enum, unique

from lib.services.pump.pump_interface import PumpInterface

logger = logging.getLogger(__name__)

"""
##### This pump speaks ASCII for all serial commands #####

Valid communications response always begins with /0 (host address)
Any individual pump module can be queried/commanded with its number, e.g. /1
After /0, the backtick (`) indicates "not busy", @ means "busy", and any other
letter means the module is reporting an error (this is the status byte)
After the status byte, there can also be a return value in response to a query

Commands (all require an "R" after the command to run)
"W4R" will initialize the syringe to the start position, must be run at startup

"AnR" will command an absolute move to n steps from the valve
"DnR" will dispense n steps toward the valve
"PnR" will aspirate n steps away from the valve

"IR" switches valve to input position (port A -> syringe)
"OR" switches valve to output position (syringe -> port B)
"BR" switches valve to bypass position (port A -> port B)

Queries (do not require an "R")
"?" queries syringe position, given in absolute steps from the valve
"?8" queries valve status, with 1 == input, 2 == bypass, 3 == output

Example pump response (to command "?"):
b'/0`24000'
Indicates host communication is valid (/0), the pump module is ready (`),
and gives the current syringe position (24000).
"""

@unique
class ValveStates(Enum):
    """Enum values to store the pump's encoding of states of the valve. The
    values 1,2,3 are actually what gets sent back in the message to denote
    these states.
    """
    INPUT = 1
    BYPASS = 2
    OUTPUT = 3


class VersaPumpV6(PumpInterface):
    """Serial interface for Norgren Kloehn Versa Pump V6, 55 series.

    Args:
        serial_port_loc (str): location of the serial port on the host.
            Defaults to /dev/ttyUSB0, which is the port assigned on a linux
            host when it's the only device plugged in.
        baud_rate (int): baudrate for the serial connection. Defaults to 9600
            since this is the pump's default setting.
        serial_timeout (int): timeout (in seconds) after which the serial
            port will be closed if no message is received. Defaults to 2.

    Returns:
        None.
    """
    def __init__(self, serial_port_loc: str = '/dev/ttyUSB0',
                    baud_rate: int = 9600, serial_timeout: int = 2) -> None:
        super().__init__()

        self.serial_port_loc = serial_port_loc
        self.baud_rate = baud_rate
        self.serial_timeout = serial_timeout

        # Pump protocol uses FF hex as end-of-packet character
        self.end_packet_char = b'\xff'
        # Pump protocol uses 03 hex as end-of-response character
        self.end_response_char = b'\x03'

        # Number of fill-empty cycles for syringe washing routine
        self.wash_cycles = 3

        # Syringe size in liters, ours is currently 2.5mL
        self.syringe_size_liters_ideal = 0.0025

        # Correction for approx. 1% error seen across the range
        self.syringe_size_liters_calib = 0.002478

        # Create range object for all valid syringe positions
        self.syringe_position_min = 0
        self.syringe_position_max = 48000
        self.syringe_position_range = range(self.syringe_position_min,
                                            self.syringe_position_max + 1)

        # Get liters per step of the syringe to make calculations easier
        self.liters_per_step = (self.syringe_size_liters_calib /
                                    self.syringe_position_max)

    def open_serial_port(self, port: str = None) -> bool:
        """Opens serial communication to the pump.

        Args:
            port (str): port location on the host. Class default will be
                used if not specified.

        Returns:
            bool: True if the connection was successful, False otherwise.
        """
        if port:
            self.serial_port_loc = port

        logger.info(f"Connecting to pump on port {self.serial_port_loc}...")

        try:
            self.serial_port = serial.Serial(
                port = self.serial_port_loc,
                baudrate = self.baud_rate,
                bytesize = serial.EIGHTBITS,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                timeout = self.serial_timeout
            )
            logger.info(f"Pump serial port open: {self.serial_port}")
            return True
        except serial.SerialException as e:
            logger.error(f"Connection failed with error: {e}")
            return False

    def initialize_pump(self) -> dict:
        """Sends the serial command to initialize the pump.

        Required after any loss of power or power-cycle, and will
        reset the syringe position to 0; be cautious about calling this
        if the syringe is full.

        Args:
            None.

        Returns:
            dict: {"host_ready": (bool), "module_ready": (bool), "msg": (str)}
        """
        cmd = "W4R"
        res_dict = self._send_pump_command(cmd)
        return res_dict

    def check_module_ready(self) -> bool:
        """Checks if the pump module is ready to execute another command.

        Args:
            None.

        Returns:
            bool: True if ready, False if busy.
        """
        cmd = ""
        res_dict = self._send_pump_command(cmd)
        return res_dict["module_ready"]

    def check_volume_available(self, volume: float) -> bool:
        """Compares the requested volume (in liters) to the available volume.

        This function converts liters to steps to do the calculations in the
        pump's native units.

        Args:
            volume (float): the volume (in liters) requested for the next
                titration step.

        Returns:
            bool: True if the volume is available, False otherwise.
        """
        steps_requested = self.liters_to_steps(volume)
        current_position = self.get_syringe_position()
        return current_position > steps_requested

    def get_syringe_position(self) -> int:
        """Gets the current position (in steps) of the syringe.

        Args:
            None.

        Returns:
            int: position in steps.
        """
        cmd = "?"
        res_dict = self._send_pump_command(cmd)
        syringe_position = int(res_dict["msg"])
        return syringe_position

    def set_syringe_position(self, pos: int) -> dict:
        """Requests a move of the syringe to an absolute position.

        The requested position must be between the minimum and maximum step
        count for the syringe in use.

        Args:
            pos (int): the requested position (in steps).

        Returns:
            dict: {"host_ready": (bool), "module_ready": (bool), "msg": (str)}
        """
        if not pos in self.syringe_position_range:
            raise ValueError(f"Invalid position {pos}.")

        cmd = f"A{pos}R"
        res_dict = self._send_pump_command(cmd)
        return res_dict

    def get_valve_state(self) -> ValveStates:
        """Checks if the valve is in input, bypass, or output mode.

        Args:
            None.

        Returns:
            ValveStates: enum object representing input/bypass/output.
        """
        cmd = "?8"
        res_dict = self._send_pump_command(cmd)
        valve_state_raw = int(res_dict['msg'])
        return ValveStates(valve_state_raw)

    def set_valve_state(self, state: ValveStates) -> dict:
        """Requests a change of valve state.

        Args:
            state (ValveStates): enum object representing input/bypass/output.

        Returns:
            dict: {"host_ready": (bool), "module_ready": (bool), "msg": (str)}
        """
        if not type(state) == ValveStates:
            raise ValueError(f"Invalid state {state}.")

        if state == ValveStates.INPUT:
            cmd = "IR"
        if state == ValveStates.BYPASS:
            cmd = "BR"
        if state == ValveStates.OUTPUT:
            cmd = "OR"
        res_dict = self._send_pump_command(cmd)
        return res_dict

    def fill(self) -> dict:
        """Fills the syringe by moving to the maximum position.

        Args:
            None.

        Returns:
            dict: {"host_ready": (bool), "module_ready": (bool), "msg": (str)}
        """
        valve_state = self.get_valve_state()
        if not valve_state == ValveStates.INPUT:
            set = self.set_valve_state(state=ValveStates.INPUT)

        while not self.check_module_ready():
            time.sleep(0.25)

        cmd = f"A{self.syringe_position_max}R"
        res_dict = self._send_pump_command(cmd)
        return res_dict

    def empty(self) -> dict:
        """Empties the syringe by moving to the minimum position.

        Args:
            None.

        Returns:
            dict: {"host_ready": (bool), "module_ready": (bool), "msg": (str)}
        """
        valve_state = self.get_valve_state()
        if not valve_state == ValveStates.OUTPUT:
            set = self.set_valve_state(state=ValveStates.OUTPUT)

        while not self.check_module_ready():
            time.sleep(0.25)

        cmd = f"A{self.syringe_position_min}R"
        res_dict = self._send_pump_command(cmd)
        return res_dict

    def wash(self) -> dict:
        """Runs a specified number of fill-empty cycles to wash the syringe.

        Args:
            None.

        Returns:
            dict: {"host_ready": (bool), "module_ready": (bool), "msg": (str)}
        """
        last_res = None
        for _ in range(self.wash_cycles):
            fill_res_dict = self.fill()
            last_res = fill_res_dict
            while not self.check_module_ready():
                time.sleep(0.25)

            empty_res_dict = self.empty()
            last_res = empty_res_dict
            while not self.check_module_ready():
                time.sleep(0.25)
        return last_res

    def liters_to_steps(self, volume: float) -> int:
        """Converts a volume (in liters) to steps on the syringe.

        Args:
            volume (float): volume (in liters) to convert to steps.

        Returns:
            int: step count equivalent to the provided volume.
        """
        return int(volume / self.liters_per_step)

    def aspirate(self, volume: float) -> dict:
        """Draws a specific volume (in liters) into the syringe.

        Note that this is a relative volume (i.e. from wherever the syringe
        is currently positioned), and repeated calls to this method will be
        additive rather than starting from 0.

        Args:
            volume (float): volume (in liters) to draw into the syringe.

        Returns:
            dict: {"host_ready": (bool), "module_ready": (bool), "msg": (str)}
        """
        steps = self.liters_to_steps(volume)

        if not steps in self.syringe_position_range:
            raise ValueError(f"Invalid position {steps}.")

        valve_state = self.get_valve_state()
        if not valve_state == ValveStates.INPUT:
            set = self.set_valve_state(state=ValveStates.INPUT)

        while not self.check_module_ready():
            time.sleep(0.25)

        cmd = f"P{steps}R"
        res_dict = self._send_pump_command(cmd)
        return res_dict

    def dispense(self, volume: float) -> dict:
        """Dispenses a specific volume (in liters) from the syringe.

        Note that this is a relative volume (i.e. from wherever the syringe
        is currently positioned), and repeated calls to this method will be
        additive rather than starting from 0.

        Args:
            volume (float): volume (in liters) to dispense from the syringe.

        Returns:
            dict: {"host_ready": (bool), "module_ready": (bool), "msg": (str)}
        """
        steps = self.liters_to_steps(volume)

        if not steps in self.syringe_position_range:
            raise ValueError(f"Invalid position {steps}.")

        valve_state = self.get_valve_state()
        if not valve_state == ValveStates.OUTPUT:
            set = self.set_valve_state(state=ValveStates.OUTPUT)

        while not self.check_module_ready():
            time.sleep(0.25)

        cmd = f"D{steps}R"
        res_dict = self._send_pump_command(cmd)
        return res_dict

    def _build_serial_command(self, cmd: str) -> bytes:
        """Uses Norgren-specific formatting and converts to bytes.

        Args:
            cmd (str): the command to be encoded, e.g. "A24000R".

        Returns:
            bytes: ascii-encoded command, e.g. b'/1A24000R\r'.
        """
        return f"/1{cmd}\r".encode("ascii")

    def _send_pump_command(self, cmd: str) -> dict:
        """Sends an encoded serial command and returns the decoded response.

        Args:
            cmd (str): the command to be encoded, e.g. "A24000R".

        Returns:
            dict: {"host_ready": (bool), "module_ready": (bool), "msg": (str)}
        """
        serial_cmd = self._build_serial_command(cmd)
        self.serial_port.write(serial_cmd)

        res_bytes = self.serial_port.read_until(expected=self.end_packet_char)
        res_bytes_cleaned = res_bytes.split(self.end_response_char)[0]
        return self._check_response(res_bytes_cleaned)

    def _check_response(self, res: bytes) -> dict:
        """Helper function to parse data from serial messages.

        Args:
            res (bytes): encoded response coming from the pump. See
                above for examples.

        Returns:
            dict: {"host_ready": (bool), "module_ready": (bool), "msg": (str)}
        """
        # Decode the response and strip whitespace
        res_decoded = res.decode("ascii").rstrip()

        # Check if communication with the host was successful
        host_status = res_decoded[:2]
        host_ready = True if host_status == '/0' else False

        # Check if the pump module is ready to take commands
        module_status = res_decoded[2]
        module_ready = True if module_status == '`' else False

        # Parse the response message
        msg = res_decoded[3:]
        return {"host_ready": host_ready, "module_ready": module_ready,
                    "msg": msg}
