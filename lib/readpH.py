import serial
import serial.tools.list_ports


def readpH(s):

    s.reset_input_buffer()

    serialString = ""
    while 1:
        if s.in_waiting > 0:
            serialString = s.readline()
            try:
                serialString = serialString.decode("Ascii")
                arr = serialString.split(",")
                if serialString.find("\rA211 pH") != -1:
                    i = arr.index(" mV")
                    emf = arr[i - 1]
                    pH = arr[i - 3]
                    return emf, pH
            except:
                pass
