import time
import serial

# from lib.services.ph.ph_interface import pHInterface

"""
***pH meter speaks ASCII for serial commands***

Commands given in the form of "<OPCODE> <OPERAND>\r"



"""

class OrionStarA215:
    def __init__(self) -> None:
        # super().__init__()

        self.SERIAL_PORT_LOC = '/dev/ttyACM0'
        self.BAUD_RATE = 9600
        self.SERIAL_TIMEOUT = 5

        self.serial_port = serial.Serial(
            port = self.SERIAL_PORT_LOC,
            baudrate = self.BAUD_RATE,
            bytesize = serial.EIGHTBITS,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            timeout = self.SERIAL_TIMEOUT
        )
        print(f"Serial port open: {self.serial_port}")

    def build_serial_command(self, cmd: str) -> bytes:
        """Uses Thermo-specific formatting and converts to bytes"""
        return f"{cmd}\r".encode("ascii")

    def send_meter_command(self, cmd:str) -> dict:
        """
        Builds and sends an encoded serial command and returns the decoded
        response.
        """
        serial_cmd = self.build_serial_command(cmd)
        self.serial_port.write(serial_cmd)
        #
        # time.sleep(0.5)
        res_bytes = self.serial_port.read_until(expected=b'---')
        print(res_bytes)

    def check_response(self, res: bytes) -> dict:
        """ Serial communications helper; schema defined in pH meter manual """
        pass




if __name__ == '__main__':
    phmeter = OrionStarA215()
    phmeter.send_meter_command("GETMEAS")
