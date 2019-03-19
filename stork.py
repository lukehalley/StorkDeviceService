# pylint: disable=import-error, no-member

# pack temp and humidity and status and light in 32 bits

from network import Sigfox
from pytrack import Pytrack
import urequests as requests
from L76GNSS import L76GNSS
from LIS2HH12 import LIS2HH12
import socket
import time
import pycom
import struct

# Imports For Acc
import gc

# Create instance of the Pytrack to access its functions
py = Pytrack()

# Set the gps port and its timeout
gps = L76GNSS(py, timeout=60)

# Set the accelerator port
acc = LIS2HH12()

# Set the timer 0
init_timer = time.time()

# Fake Lat and Long to use indoors
fakeLat = 26.13454
fakeLong = -152.45367

# Set the status code to be all ok to start off.
statusCode = 0

# initalise Sigfox for RCZ1 (Europe) (You may need a different RCZ Region)
# sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1) <- CODE DOESN'T RUN IF THIS IS RAN

# Set the sigfox socker
s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)

# Disables heartbeat to enable the LED to be used
pycom.heartbeat(False)

# Post all parameters to the Sigfox backend
def postData(latitude, longitude):
    try:
        prg = "SENDING THE FOLLOWING DATA -> GPS: {} : {}".format(latitude, longitude)
        print(prg)
        print("SENDING DATA")
        pycom.rgbled(0x7F0000)
        s.send(struct.pack("<f", float(latitude)) + struct.pack("<f", float(longitude)))
        # s.send(struct.pack("s", str(storkCode)) + "f", float(latitude)) + struct.pack("f", float(longitude) + struct.pack("c", char(statusCode)))
        print("DATA SENT!")
        pycom.rgbled(0xB31DDC)  # green
    except Exception as e:
        print("Failed to get Lat Long: " + e)
        pass


postData(fakeLat, fakeLong)
