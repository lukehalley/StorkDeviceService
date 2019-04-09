# pylint: disable=import-error, no-member

# lat::float:32:little-endian lng::float:32:little-endian temp::uint:16:little-endian hum::uint:16:little-endian stat::char:1

# {
#   "snr" : "{snr}",
#   "lat": "{lat}",
#   "lng": "{lng}",
#   "device" : "{device}",
#   "avgSnr" : "{avgSnr}",
#   "rssi" : "{rssi}",
#   "location" : {"type" : "Point", "coordinates" : [{customData#lat}, {customData#lng}]},
#   "temperature" : "{customData#temp}",
#   "humidity" : "{customData#hum}",
#   "status" : "{customData#stat}"
# }


# ------------------ Imports ------------------
from network import Sigfox
from pytrack import Pytrack
import urequests as requests
from L76GNSS import L76GNSS
from LIS2HH12 import LIS2HH12
import socket
import binascii
import time
import pycom
import struct
import gc
from machine import SD

# ------------------ DEVICE SETUP ------------------
# Create instance of the Pytrack to access its functions
py = Pytrack()

# Set the gps port and its timeout
gps = L76GNSS(py, timeout=60)

# Set the accelerator port
acc = LIS2HH12()

# Set the status code to be all ok to start off.
statusCode = 15

# Set the sigfox socker
s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)

# Disables heartbeat to enable the LED to be used
pycom.heartbeat(False)

# ------------------ TIMER SETUP ------------------
# Set the timer 0
init_timer = time.time()

# ------------------ DATA SETUP ------------------
# Fake Lat and Long to use indoors
fakeLat = 40.71427
fakeLong = -74.00597

# Fake Lat and Long to use indoors
temp = 34
hum = 26

# Array to collect two pitch and roll values to compare
pitchValues = []
rollValues = []

# Setting the mishandle limits
okLimit = 30
warningLimit = 55
dangerLimit = 100

# Mishandle Counts
warnCount = 0
dangerCount = 0

# Mishandle Boolean
mishandle = False

# Variable to track the minutes that have passed
minInt = 0

# Send every n mins - WARNING: Should be 10 minutes to meet the Sigfox sending limits
sendCycle = 0

# GPS Fix Status
fix = False

# Send to Sigfox - set to True in production
post = True

# Boolean to decide if we should wait for GPS (Testing)
waitForGPS = False

sleeptime = 100

# Print Sigfox Device ID
print("Stork Code: ", binascii.hexlify(sigfox.id()))

# ------------------ FUNCTIONS ------------------
# Post all parameters to the Sigfox backend
def postData(latitude, longitude):
    try:
        prg = "SENDING THE FOLLOWING DATA -> GPS: {} : {} - TEMP: {} HUM: {}".format(
            latitude, longitude, temp, hum
        )
        print(prg)
        print("SENDING DATA")
        pycom.rgbled(0x7F0000)

        longByteArray = bytearray(struct.pack("<f", float(latitude)))
        longByteArray.extend(bytearray(struct.pack("<f", float(longitude))))
        longByteArray.extend(bytearray(struct.pack("<B", temp)))
        longByteArray.extend(bytearray(struct.pack("<B", hum)))
        longByteArray.extend(bytearray(struct.pack("<B", statusCode)))

        s.send(longByteArray)
        # s.send(struct.pack("s", str(storkCode)) + "f", float(latitude)) + struct.pack("f", float(longitude) + struct.pack("c", char(statusCode)))
        print("DATA SENT!")
        pycom.rgbled(0xB31DDC)  # green
    except Exception as e:
        print("Failed to get Lat Long: " + e)
        pass


# ------------------ MAIN LOOP ------------------
while True:
    # Current time
    final_timer = time.time()
    # timeElapsed is the amount of seconds which have passed
    timeElapsed = final_timer - init_timer

    # If 60 seconds has passed and "sendCycle" mins (sendCycle is set to 10 mins normally as Sigfox allows a message to be sent every 10 minutes) has NOT passed.
    if (timeElapsed >= 60) and (minInt < sendCycle):
        # Reset the timer
        init_timer = time.time()
        # Increment the minute counter
        minInt += 1
        print("{} Minutes Has Passed!".format(minInt))
        print(
            "Mishandle Counts - Warning Count: {} Danger Count: {} ".format(
                warnCount, dangerCount
            )
        )
        # time.sleep(10)
    # If "sendCycle" (sendCycle is set to 10 mins normally as Sigfox allows a message to be sent every 10 minutes) mins has passed
    elif minInt >= sendCycle:
        print("{} Minutes Has Passed!".format(minInt))
        print(
            "Mishandle Counts - Warning Count: {} Danger Count: {} ".format(
                warnCount, dangerCount
            )
        )
        # If one or more dangerous mishandle has been detected or more than 5 warning (mishandles of medium severity) mishandles
        if (dangerCount > 0) or (warnCount >= 5):
            # Set that there was a mishandle
            mishandle = True
            print(
                "Mishandle Limit Exceeded - Sending Mishandle As {}!".format(mishandle)
            )
        else:
            # Set that was not a mishandle
            mishandle = False
            print(
                "Mishandle Limit Not Exceeded - Sending Mishandle As {}!".format(
                    mishandle
                )
            )
        # SEND CURRENT GPS, TEMP, HUMIDITY & STATUS
        print("Getting GPS Position...")
        coord = gps.coordinates()

        if waitForGPS:
            while coord == (None, None):
                pycom.rgbled(0x7F0000)
                print("Waiting for GPS...")
                coord = gps.coordinates()
                print(coord)

        lat, lng = coord

        if not lat is None and not lng is None:  # Have a GPS fix
            if fix:
                print("GPS Lock Acquired! - Sending Real GPS Data!")
                pycom.rgbled(0x7F7F00)  # YELLOW
                if post:
                    print("Posting REAL data!")
                    postData(lat, lng)
                else:
                    print("postToSigfox set to False - not posting REAL data!")
                fix = True
            print("{} {}".format(lat, lng))
        else:  # No GPS fix
            if not fix:
                print("GPS signal lost or could not be locked!")
                pycom.rgbled(0x7F0000)  # RED
                if post:
                    print("Posting FAKE data!")
                    postData(fakeLat, fakeLong)
                else:
                    print("postToSigfox set to False - not posting FAKE data!")
                fix = False
        # Set the minute counter back to zero for the next "sendCycle" min cycle
        minInt = 0
        print("CYCLE DONE!!!!!! SLEEPING FOR N SECS!")
        time.sleep(sleeptime)
    # If the cycle is still active keep reading values
    else:
        # Get two pitch values and two roll values
        while len(pitchValues) <= 1 and len(rollValues) <= 1:
            # Add them to their respective
            pitchValues.append(acc.pitch())
            rollValues.append(acc.roll())
        # After getting two pitch values and two roll values
        else:
            # Get the difference between the sum of the two pitch values and the sum of the two roll values
            difference = abs(pitchValues[1] - pitchValues[0]) + abs(
                rollValues[1] - rollValues[0]
            )
            print("Difference: {}".format(difference))
            # Detect a 002 mishandle (mishandles of medium severity)
            if difference > okLimit and difference < dangerLimit:
                print("Mishandle Warning: 002")
                # Increment the count of the 002 mishandles detected
                warnCount += 1
                time.sleep(0.5)
            # Detect a 003 mishandle (mishandles of high severity)
            elif difference > warningLimit:
                # Increment the count of the 002 mishandles detected
                print("Mishandle Danger: 003")
                dangerCount += 1
                time.sleep(0.5)
            else:
                pass
        # Clear the pitch and roll values for the next two that will be read in
        pitchValues.clear()
        rollValues.clear()
