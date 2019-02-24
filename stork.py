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

py = Pytrack()
gps = L76GNSS(py, timeout=60)

init_timer = time.time()
acc = LIS2HH12()

fakeLat = 26.13454
fakeLong = -152.45367

storkCode = "0002"
statusCode = 2

# initalise Sigfox for RCZ1 (Europe) (You may need a different RCZ Region)
# sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)

s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)

# ------------------ LED SETUP ------------------
# Disables heartbeat to enable the LED to be used
pycom.heartbeat(False)

# Post an location to the Wia cloud via Sigfox backend
def post_location(latitude, longitude):
    pitch = acc.pitch()
    roll = acc.roll()
    try:
        prg = "SENDING THE FOLLOWING DATA -> GPS: {} : {} -> Pitch: {} Roll: {}".format(
            latitude, longitude, pitch, roll
        )
        print(prg)
        print("SENDING DATA")
        pycom.rgbled(0x7F0000)  # red
        s.send(struct.pack("<f", float(latitude)) + struct.pack("<f", float(longitude)))
        # s.send(struct.pack("s", str(storkCode)) + "f", float(latitude)) + struct.pack("f", float(longitude) + struct.pack("c", char(statusCode)))
        print("DATA SENT!")
        pycom.rgbled(0xB31DDC)  # green
    except Exception as e:
        print("Failed to get Lat Long: " + e)
        pr = "Pitch:  {} Roll: {}".format(pitch, roll)
        print(pr)
        pass


# main loop
# while True:
# final_timer = time.time()
# diff = final_timer - init_timer
# coord = gps.coordinates()
# fakeLat, fakeLong = coord
post_location(fakeLat, fakeLong)
# init_timer = time.time()
# time.sleep(2.5)
# If the GPS has coordinates and 15 minites has past. Post the location data
# if diff < 15:
#     pycom.rgbled(0x1DDCDC)  # blue
#     # lat, lng = coord
#     post_location(fakeLat, fakeLong)
#     init_timer = time.time()
