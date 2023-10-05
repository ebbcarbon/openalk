import time
import serial
from enum import Enum, auto

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


class ValveStates(Enum):
    INPUT = 1
    BYPASS = 2
    OUTPUT = 3

class ValvePorts(Enum):
    A = auto()
    B = auto()
    S = auto()


class NorgrenPump(PumpInterface):
    def __init__(self) -> None:
        super().__init__()

        self.SERIAL_PORT_LOC = '/dev/ttyUSB0'
        self.BAUD_RATE = 9600
        self.SERIAL_TIMEOUT = 2

        self.steps_to_ml_factor = None

        self.SYRINGE_POSITION_MIN = 0
        self.SYRINGE_POSITION_MAX = 48000

        """ Most of these parameters are defined in the pump manual """
        self.serial_port = serial.Serial(
            port = self.SERIAL_PORT_LOC,
            baudrate = self.BAUD_RATE,
            bytesize = serial.EIGHTBITS,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            timeout = self.SERIAL_TIMEOUT
        )

    def initialize_pump(self) -> dict:
        cmd = "W4R"
        res_dict = self.send_pump_command(cmd)
        return res_dict

    def get_syringe_position(self) -> int:
        """Need to parse response to return int syringe position"""
        cmd = "?"
        res_dict = self.send_pump_command(cmd)
        print(res_dict)
        return

    def set_syringe_position(self, pos: int) -> dict:
        """Need to make sure 'pos' is within the acceptable range"""
        cmd = f"A{pos}R"
        res_dict = self.send_pump_command(cmd)
        return res_dict

    def get_valve_state(self) -> ValveStates:
        """Need to parse response to return ValveState"""
        cmd = "?8"
        res_dict = self.send_pump_command(cmd)
        print(res_dict)
        return

    def set_valve_state(self, state: ValveStates) -> dict:
        """Need to make sure 'state' is valid"""
        if state == ValveStates.INPUT:
            cmd = "IR"
        if state == ValveStates.BYPASS:
            cmd = "BR"
        if state == ValveStates.OUTPUT:
            cmd = "OR"
        res_dict = self.send_pump_command(cmd)
        return res_dict

    def fill_syringe(self) -> dict:
        """From where?"""
        cmd = f"A{self.SYRINGE_POSITION_MAX}R"
        res_dict = self.send_pump_command(cmd)
        return res_dict

    def empty_syringe(self) -> dict:
        """To where?"""
        cmd = f"A{self.SYRINGE_POSITION_MIN}R"
        res_dict = self.send_pump_command(cmd)
        return res_dict

    def wash_syringe(self) -> dict:
        """With what?"""
        wash_cycles = 3
        """TODO: blocking logic here"""
        for _ in range(wash_cycles):
            fill_res_dict = self.fill_syringe()
            empty_res_dict = self.empty_syringe()
        return {}

    def aspirate(self, steps: int, port: ValvePorts) -> dict:
        """From where?"""
        """Need to make sure 'steps' and 'port' are valid"""
        cmd = f"P{steps}R"
        res_dict = self.send_pump_command(cmd)
        return res_dict

    """
    Maybe the res_dict should just be an internal object for verification,
    and all the individual methods just return a bool?
    """

    """
    Same thing with the ValveStates, should the user need to know about them?
    """

    def dispense(self, steps: int, port: ValvePorts) -> dict:
        """To where?"""
        """Need to make sure 'steps' and 'port' are valid"""
        cmd = f"D{steps}R"
        res_dict = self.send_pump_command(cmd)
        return res_dict

    def send_pump_command(self, cmd: str) -> dict:
        """
        Builds and sends an encoded serial command and returns the decoded
        response in an easily accessible way.
        """
        serial_cmd = self.build_serial_command(cmd)
        self.serial_port.write(serial_cmd)
        res_bytes = self.serial_port.readline().split()[0]
        return self.check_response(res_bytes)

    def build_serial_command(self, cmd: str) -> bytes:
        """Uses Norgren-spcific string formatting and converts to bytes"""
        return f"/1{cmd}\r".encode("ascii")

    def check_response(self, res: bytes) -> dict:
        """ Serial communications helper; schema defined in pump manual """
        res_decoded = res.decode("ascii").rstrip()
        host_status = res_decoded[:2]
        module_status = res_decoded[2]
        msg = res_decoded[3:]
        return {"host_status": host_status, "module_status": module_status,
                    "msg": msg}
