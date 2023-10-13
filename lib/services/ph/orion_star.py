import time
import serial

from lib.services.ph.ph_interface import pHInterface

"""
***pH meter speaks ASCII for serial commands***

Make sure the "Export Data" and "DataLog" settings on the meter are both off,
this will ensure the buffer is clear for request-response transactions.

Commands given in the form of "<OPCODE> <OPERAND>\r"

We should really only need to take data in from the meter at this point,
so use "GETMEAS \r"

"""

class OrionStarA215(pHInterface):
    def __init__(self) -> None:
        super().__init__()

        self.SERIAL_PORT_LOC = '/dev/ttyACM0'
        self.BAUD_RATE = 9600

        # Be careful about changing this; had to bump to 4 to avoid chopping
        # up the serial return message
        self.SERIAL_TIMEOUT = 4

        print(f"Connecting to pH meter on port {self.SERIAL_PORT_LOC}...")

        self.serial_port = serial.Serial(
            port = self.SERIAL_PORT_LOC,
            baudrate = self.BAUD_RATE,
            bytesize = serial.EIGHTBITS,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            timeout = self.SERIAL_TIMEOUT
        )
        if self.serial_port.is_open:
            print(f"pH meter serial port open: {self.serial_port}")

    def get_measurement(self) -> dict:
        cmd = "GETMEAS"
        res_dict = self.send_meter_command(cmd)
        return res_dict

    def build_serial_command(self, cmd: str) -> bytes:
        """Uses Thermo-specific formatting and converts to bytes"""
        return f"{cmd}\r".encode("ascii")

    def send_meter_command(self, cmd: str) -> dict:
        """
        Builds and sends an encoded serial command and returns the decoded
        response.
        """
        serial_cmd = self.build_serial_command(cmd)
        self.serial_port.write(serial_cmd)

        # Meter protocol uses > as the end-of-response character
        res_bytes = self.serial_port.read_until(expected=b'\r>')
        return self.check_response(res_bytes)

    def check_response(self, res: bytes) -> dict:
        """ Serial communications helper; schema defined in pH meter manual """
        res_decoded = res.decode("ascii").rstrip().splitlines()[3]

        # Split the response and take just the channel values
        channel_values_raw = res_decoded.split('---')[1]
        # Split the channel values and take pH, mV, and temp
        channel_values_list = channel_values_raw.split(',')
        return {"pH": channel_values_list[3], "mV": channel_values_list[5],
                    "temp": channel_values_list[7]}
