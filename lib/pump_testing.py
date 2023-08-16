import serial
import time

PUMP_PORT = "/dev/ttyUSB1" #subject to change depending on the type of computer being used
BAUD_RATE = 9600
SERIAL_TIMEOUT = 2


def write_cmd(port, base_cmd):
    """
    Write the given cmd to the given port
    port should be an open serial port to the pump device
    base_cmd should look like 'D1200' -- don't include the '/1' header or the trailing '\r'
    """
    print(f"Writing command to pump: {base_cmd}")

    # All cmds are preceeded by '/', then the address, which we always assume to be 1 here
    # all cmds are separated by a carriage return '\r'
    cmd = f"/1{base_cmd}\r"
    length = port.write(bytes(cmd, "utf-8"))

    # Docs indicate we can move too fast -- 8 commands a second is about all the device chan handle
    # manual sleep after each command, and then a read
    time.sleep(0.150)
    # verify that we actually wrote cmd
    assert length == len(cmd)
    read_response(port)


def read_response(port):
    """
    Read a response from the port
    """
    response = port.readline()
    print(f"Read pump response: |{response}|")


def pump_test():
    serial_port = serial.Serial(PUMP_PORT, baudrate=BAUD_RATE, timeout=SERIAL_TIMEOUT)

    write_cmd(serial_port, "?")
    # We might want to include this in the write_cmd -- docs indicate we should send this empty
    # string and look for the 'ready' ("`") response
    write_cmd(serial_port, "")
    # write_cmd(serial_port, '?31')
    # write_cmd(serial_port, '')
    # write_cmd(serial_port, '~V')
    # write_cmd(serial_port, '')
    # write_cmd(serial_port, '?8')
    # write_cmd(serial_port, '')
    # write_cmd(serial_port, '?2')
    # write_cmd(serial_port, '?3')

    # Docs indicate W4 should be the first command we send, to initialize
    write_cmd(serial_port, "W4")
    time.sleep(1)
    write_cmd(serial_port, "")
    write_cmd(serial_port, "A24000")
    write_cmd(serial_port, "")
    time.sleep(5)

    # write_cmd(serial_port, 'o3')
    # time.sleep(3)


if __name__ == "__main__":
    main()
