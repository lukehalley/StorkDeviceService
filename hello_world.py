from network import Sigfox
from time import sleep
import socket
import sys
import pycom

# init Sigfox for RCZ1 (Europe)
sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)

# create a Sigfox socket
s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)

# make the socket blocking
s.setblocking(True)

# configure it as uplink only
s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)

pycom.heartbeat(False)

# count = 0
# while (count < 10):
#    s.send("Luke!")
#    count = count + 1
#    pycom.rgbled(0x7f0000)
#    sleep(3000)
#    pycom.rgbled(0x7f7f00)

pycom.rgbled(0x7f0000)
s.send("Luke!")
pycom.rgbled(0x007f00)

machine.Pin('P14').value()
