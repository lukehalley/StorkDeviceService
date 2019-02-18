from network import Sigfox
from pytrack import Pytrack
import urequests as requests
from L76GNSS import L76GNSS
import socket
import time
import pycom
import struct

py = Pytrack()
gps = L76GNSS(py, timeout=60)

init_timer = time.time()

# print("connecting to Sigfox")
# init Sigfox for RCZ1 (Europe)
# sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)

# create a Sigfox socket
# s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)
# make the socket blocking
# s.setblocking(True)

# s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)

# Post an location to the Wia cloud via Sigfox backend
def post_location(latitude, longitude):
    try:
        print(str(latitude), ":", str(longitude))
        # s.send(struct.pack('f',float(latitude)) + struct.pack('f',float(longitude)))
    except:
        print("Failed to get lat long")
        pass

# main loop
while True:
    final_timer = time.time()
    diff = final_timer - init_timer
    # Get coordinates from pytrack
    coord = gps.coordinates()

    lat, lng = coord
    post_location(lat, lng)
    init_timer = time.time()
    time.sleep(5) 
    # If the GPS has coordinates and 15 minites has past. Post the location data
    # if not coord == (None, None) and diff < 15:
    #     lat, lng = coord
    #     post_location(lat, lng)
    #     init_timer = time.time()