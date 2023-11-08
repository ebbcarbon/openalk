import time
import serial
from enum import Enum, unique

from lib.services.pump.pump_interface import PumpInterface


"""
***Pump speaks ASCII for serial commands***

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
"""

@unique
class ValveStates(Enum):
    INPUT = 1
    BYPASS = 2
    OUTPUT = 3


class VersaPumpV6(PumpInterface):
    '''
    Interface for the Norgren Kloehn Versa Pump 6, 55 series.
    Our device shows P/N 55022, and is the 48k step version.
    '''
    def __init__(self) -> None:
        super().__init__()

        self.SERIAL_PORT_LOC = '/dev/ttyUSB0'
        self.BAUD_RATE = 9600
        self.SERIAL_TIMEOUT = 2

        self.WASH_CYCLES = 3

        # Syringe size in liters, ours is currently 2.5mL
        self.SYRINGE_SIZE_L_IDEAL = 0.0025

        # Correction for approx. 1% error seen across the range
        self.SYRINGE_SIZE_L_CALIB = 0.002478

        self.SYRINGE_POSITION_MIN = 0
        self.SYRINGE_POSITION_MAX = 48000
        self.SYRINGE_POSITION_RANGE = range(self.SYRINGE_POSITION_MIN,
                                            self.SYRINGE_POSITION_MAX + 1)

        self.LITERS_PER_STEP = (self.SYRINGE_SIZE_L_CALIB /
                                    self.SYRINGE_POSITION_MAX)

        print(f"Connecting to pump on port {self.SERIAL_PORT_LOC}...")

        """ Most of these parameters are defined in the pump manual """
        self.serial_port = serial.Serial(
            port = self.SERIAL_PORT_LOC,
            baudrate = self.BAUD_RATE,
            bytesize = serial.EIGHTBITS,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            timeout = self.SERIAL_TIMEOUT
        )
        if self.serial_port.is_open:
            print(f"Pump serial port open: {self.serial_port}")

    def initialize_pump(self) -> dict:
        cmd = "W4R"
        res_dict = self._send_pump_command(cmd)
        return res_dict

    def check_module_ready(self) -> bool:
        cmd = ""
        res_dict = self._send_pump_command(cmd)
        return res_dict["module_ready"]

    def check_volume_available(self, volume: float) -> bool:
        steps_requested = self.liters_to_steps(volume)
        current_position = self.get_syringe_position()
        return current_position > steps_requested

    def get_syringe_position(self) -> int:
        cmd = "?"
        res_dict = self._send_pump_command(cmd)
        syringe_position = int(res_dict["msg"])
        return syringe_position

    def set_syringe_position(self, pos: int) -> dict:
        if not pos in self.SYRINGE_POSITION_RANGE:
            raise ValueError(f"Invalid position {pos}.")

        cmd = f"A{pos}R"
        res_dict = self._send_pump_command(cmd)
        return res_dict

    def get_valve_state(self) -> ValveStates:
        cmd = "?8"
        res_dict = self._send_pump_command(cmd)
        valve_state_raw = int(res_dict['msg'])
        return ValveStates(valve_state_raw)

    def set_valve_state(self, state: ValveStates) -> dict:
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
        valve_state = self.get_valve_state()
        if not valve_state == ValveStates.INPUT:
            set = self.set_valve_state(state=ValveStates.INPUT)

        while not self.check_module_ready():
            time.sleep(0.25)

        cmd = f"A{self.SYRINGE_POSITION_MAX}R"
        res_dict = self._send_pump_command(cmd)
        return res_dict

    def empty(self) -> dict:
        valve_state = self.get_valve_state()
        if not valve_state == ValveStates.OUTPUT:
            set = self.set_valve_state(state=ValveStates.OUTPUT)

        while not self.check_module_ready():
            time.sleep(0.25)

        cmd = f"A{self.SYRINGE_POSITION_MIN}R"
        res_dict = self._send_pump_command(cmd)
        return res_dict

    def wash(self) -> dict:
        last_res = None
        for _ in range(self.WASH_CYCLES):
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
        return int(volume / self.LITERS_PER_STEP)

    def aspirate(self, volume: float) -> dict:
        steps = self.liters_to_steps(volume)

        if not steps in self.SYRINGE_POSITION_RANGE:
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
        steps = self.liters_to_steps(volume)

        if not steps in self.SYRINGE_POSITION_RANGE:
            raise ValueError(f"Invalid position {steps}.")

        valve_state = self.get_valve_state()
        if not valve_state == ValveStates.OUTPUT:
            set = self.set_valve_state(state=ValveStates.OUTPUT)

        while not self.check_module_ready():
            time.sleep(0.25)

        cmd = f"D{steps}R"
        res_dict = self._send_pump_command(cmd)
        return res_dict

    def _send_pump_command(self, cmd: str) -> dict:
        """
        Builds and sends an encoded serial command and returns the decoded
        response.
        """
        serial_cmd = self._build_serial_command(cmd)
        self.serial_port.write(serial_cmd)

        # Pump protocol uses FF hex as end-of-packet character
        res_bytes = self.serial_port.read_until(expected=b'\xff')
        # Pump protocol uses 03 hex as end-of-response character
        res_bytes_cleaned = res_bytes.split(b'\x03')[0]
        return self._check_response(res_bytes_cleaned)

    def _build_serial_command(self, cmd: str) -> bytes:
        """Uses Norgren-specific string formatting and converts to bytes"""
        return f"/1{cmd}\r".encode("ascii")

    def _check_response(self, res: bytes) -> dict:
        """ Serial communications helper; schema defined in pump manual """
        res_decoded = res.decode("ascii").rstrip()

        host_status = res_decoded[:2]
        host_ready = True if host_status == '/0' else False

        module_status = res_decoded[2]
        module_ready = True if module_status == '`' else False

        msg = res_decoded[3:]
        return {"host_ready": host_ready, "module_ready": module_ready,
                    "msg": msg}
