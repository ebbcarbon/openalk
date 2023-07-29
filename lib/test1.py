# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 11:48:43 2023

@author: mehak
"""
import time
from pump_module import Pump 
import serial

# pump1 = Pump()

# pump1.pump_test()
# time.sleep(1.0)

# pump1.initialization()
# time.sleep(1.0)

# pump1.fill()

# pump1.empty()

from readpH import readpH

s = serial.Serial("COM3")

emf, pH = readpH(s)

print(emf)
print(pH)
