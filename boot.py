from machine import UART
from network import Sigfox
import binascii
import machine
import os

# initalise Sigfox for RCZ1 (Europe) (You may need a different RCZ Region)
# sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)

# print Sigfox Device ID
# print("ID: ", binascii.hexlify(sigfox.id()))

# print Sigfox PAC number
# print("PAC: ", binascii.hexlify(sigfox.pac()))

uart = UART(0, baudrate=115200)
os.dupterm(uart)

machine.main("main.py")

