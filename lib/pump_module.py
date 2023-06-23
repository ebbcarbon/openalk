import serial

PUMP_PORT = '/dev/ttyUSB1'
BAUD_RATE = 9600
SERIAL_TIMEOUT = 2

def write_cmd(port, base_cmd):
    """
    Write the given cmd to the given port
    port should be an open serial port to the pump device
    base_cmd should look like 'D1200' -- don't include the '/1' header or the trailing '\r'
    """
    print(f'Writing command to pump: {base_cmd}')

    # All cmds are preceeded by '/', then the address, which we always assume to be 1 here
    # all cmds are separated by a carriage return '\r'
    cmd = f'/1{cmd}\r'
    length = port.write(f'{cmd}\r')
    # verify that we actually wrote cmd
    assert length == len(cmd)

    serial_string = port.readline()
    print(f'Read pump response: |{response}|')


def pump_test():
    serial_port =  serial.Serial(PUMP_PORT, baudrate=BAUD_RATE, timeout=SERIAL_TIMEOUT)

    write_cmd(serial_port, '?')
    write_cmd(serial_port, '?1')
    write_cmd(serial_port, '?2')
    write_cmd(serial_port, '?3')

    # Test other commands here


if __name__ == '__main__' :
    main()
