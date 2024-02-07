import serial
import logging

from lib.services.ph.ph_interface import pHInterface

logger = logging.getLogger(__name__)

"""
##### This meter speaks ASCII for all serial commands #####

Make sure the "Export Data" and "DataLog" settings on the meter are both off,
this will ensure the buffer is clear for request-response transactions.

Commands given in the form of "<OPCODE> <OPERAND>\r".

Example pH channel response:
b'GETMEAS         \r\n\r\n\rA215 pH,X51250,3.04,ABCDE,12/07/23
  09:30:40,---,CH-1,pH,4.61,pH,111.2, mV,25.0,C,89.1,%,M100,#1\n\r\r>'
"""

class OrionStarA215(pHInterface):
    """Serial interface for Orion Star A215 pH meters.

    Args:
        serial_port_loc (str): location of the serial port on the host.
            Defaults to /dev/ttyACM0, which is the port assigned on a linux
            host when it's the only device plugged in.
        baud_rate (int): baudrate for the serial connection. Defaults
            to 9600 since this is the meter's default setting.
        serial_timeout (int): timeout (in seconds) after which the serial
            port will be closed if no message is received. Defaults to 600.
            The default of 600 is important for the current functionality,
            so be careful not to change it.

    Returns:
        None.
    """
    def __init__(self, serial_port_loc: str = '/dev/ttyACM0',
                    baud_rate: int = 9600, serial_timeout: int = 600) -> None:
        super().__init__()

        self.serial_port_loc = serial_port_loc
        self.baud_rate = baud_rate
        self.serial_timeout = serial_timeout

        # Meter protocol uses > as the end-of-response character
        self.end_response_char = b'\r>'

        logger.info(f"Connecting to pH meter on port {self.serial_port_loc}...")

        self.serial_port = serial.Serial(
            port = self.serial_port_loc,
            baudrate = self.baud_rate,
            bytesize = serial.EIGHTBITS,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            timeout = self.serial_timeout
        )
        if self.serial_port.is_open:
            logger.info(f"pH meter serial port open: {self.serial_port}")

    def get_measurement(self) -> dict:
        """Polls the meter for measurements of pH, emf, and temperature.

        Args:
            None.

        Returns:
            dict: {"pH": (str), "mV": (str), "temp": (str)}
        """
        cmd = "GETMEAS"
        res_dict = self._send_meter_command(cmd)
        return res_dict

    def _build_serial_command(self, cmd: str) -> bytes:
        """Uses Thermo-specific formatting and converts to bytes.

        Args:
            cmd (str): the command to be encoded, e.g. "GETMEAS".

        Returns:
            bytes: ascii-encoded command, e.g. b'GETMEAS\r'
        """
        return f"{cmd}\r".encode("ascii")

    def _send_meter_command(self, cmd: str) -> dict:
        """Sends an encoded serial command and returns the decoded response.

        Args:
            cmd (str): the command to be encoded, e.g. "GETMEAS".

        Returns:
            dict: {"pH": (str), "mV": (str), "temp": (str)}
        """
        serial_cmd = self._build_serial_command(cmd)
        self.serial_port.write(serial_cmd)

        res_bytes = self.serial_port.read_until(
                        expected=self.end_response_char
                    )
        return self._check_response(res_bytes)

    def _check_response(self, res: bytes) -> dict:
        """Helper function to parse data from serial messages.

        Args:
            res (bytes): encoded response coming from the pH meter. See
                above for examples.

        Returns:
            dict: {"pH": (str), "mV": (str), "temp": (str)}
        """
        # Decode the response and strip leading newlines
        res_decoded = res.decode("ascii").rstrip().splitlines()[3]

        # Split the response and take just the channel values
        try:
            channel_values_raw = res_decoded.split('---')[1]
        except IndexError as e:
            logger.error(f"Invalid response from meter: {res_decoded}, Error: {e}")

        # Split the channel values and take pH, mV, and temp
        channel_values_list = channel_values_raw.split(',')
        return {"pH": channel_values_list[3], "mV": channel_values_list[5],
                    "temp": channel_values_list[7]}
