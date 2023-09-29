import serial
import time


PUMP_PORT_ADDR = "/dev/ttyUSB0"
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
    print(response)
    print(response.decode("utf-8"))
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

def initialize_pump():
    pass

def move_to_absolute_position(port, pos):
    pass

def fill_syringe():
    '''From where?'''
    pass

def empty_syringe():
    '''To where?'''
    pass

def wash():
    pass

def dispense(steps):
    pass

def aspirate(steps):
    pass

def set_valve_to_input():
    pass

def set_valve_to_output():
    pass

def check_syringe_position():
    pass

def check_valve_position():
    pass

def check_response(res):
    # Split apart decoded response string
    pass


'''
***Pump speaks ASCII only***

Valid communications response always begins with /0 (host address)
Any individual pump module can be queried/commanded with its number, e.g. /1
After /0, the backtick (`) indicates "not busy", @ means "busy", and any other
letter means the module is reporting an error (this is the status byte)
After the status byte, there can also be a return value in response to a query

Commands (all require an "R" after the command to run)
"W4" will initialize the syringe to the start position, must be run at startup

"An" will command an absolute move to n steps from the valve
"Dn" will dispense n steps toward the valve
"Pn" will aspirate n steps away from the valve

"I" switches valve to input position (port A -> syringe)
"O" switches valve to output position (syringe -> port B)
"B" switches valve to bypass position (port A -> port B)

Queries (do not require an "R")
"?" queries syringe position, given in absolute steps from the valve
"?8" queries valve status, with 1 == input, 2 == bypass, 3 == output


'''

def testing():
    port = serial.Serial(port=PUMP_PORT_ADDR, baudrate=BAUD_RATE, timeout=SERIAL_TIMEOUT)
    print(port)
    # cmd = "IR"
    cmd = "D24000R"
    # cmd = "?8"
    # cmd = "W4R"
    print(cmd)
    cmd_string = f"/1{cmd}\r"
    print(cmd_string)
    cmd_encoded = cmd_string.encode("ascii")
    print(cmd_encoded)
    port.write(cmd_encoded)
    res_encoded = port.readline().split()[0]
    res = res_encoded.decode("ascii").rstrip()

    host_status = res[:2]
    module_status = res[2]
    msg = res[3:]

    print(res)
    print(msg)


if __name__ == "__main__":
    testing()
