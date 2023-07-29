import serial
import time

#to double check which com port is in use type in conda environment 
"python -m serial.tools.list_ports"

PUMP_PORT = "COM1" #subject to change depending on laptop being used
BAUD_RATE = 9600
SERIAL_TIMEOUT = 2

class Pump():
    def __init__(self):
        self.serial_port = serial.Serial(PUMP_PORT, baudrate=BAUD_RATE, timeout=SERIAL_TIMEOUT)
        
        
    def write_cmd(self, port, base_cmd):
        """
        Write the given cmd to the given port
        port should be an open serial port to the pump device
        base_cmd should look like 'D1200R' -- don't include the '/1' header or the trailing '\r'
        R is needed for execution of the command
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
        self.read_response(port)


    def read_response(self, port):
        """
        Read a response from the port
        """
        response = port.readline()
        print(f"Read pump response: |{response}|")

    
    def pump_test(self):
        # We might want to include this in the write_cmd -- docs indicate we should send this empty
        # string and look for the 'ready' ("`") response
        self.write_cmd(self.serial_port, "")
    
    
    def initialization(self):
        self.write_cmd(self.serial_port, "W4R")
        time.sleep(1)
        
        
    def fill(self):
        self.write_cmd(self.serial_port, "A40000R")
        time.sleep(1)
        
        
    def empty(self):
        #specified output valve in here too to run the wash sequence, or can use the output_valve def prior to empty (dispenseing)
        self.write_cmd(self.serial_port, "OR") 
        time.sleep(1)
        self.write_cmd(self.serial_port, "D40000R")
        time.sleep(1)
    

    def wash(self):
        self.fill()
        time.sleep(1)
        self.empty()
        time.sleep(1)
        self.fill()
        time.sleep(1)
        self.empty()
        time.sleep(1)
        self.fill()
        time.sleep(1)
        self.empty()
        time.sleep(1)
        
        
    def input_valve(self):
        self.write_cmd(self.serial_port, "IR")
        time.sleep(1)
        
        
    def output_valve(self):
        self.write_cmd(self.serial_port, "OR")
        time.sleep(1)


# if __name__ == "__main__":
#     main()
