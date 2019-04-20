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
import machine
import struct
import gc
from os import urandom as _urandom
from machine import SD

# ------------------ DEVICE SETUP ------------------
# Create instance of the Pytrack to access its functions
py = Pytrack()

# Set the gps port and its timeout
gps = L76GNSS(py, timeout=60)

# Set the accelerator port
acc = LIS2HH12()

# Set the status code to be all ok to start off.
statusCode = 0

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
sendCycle = 10

# GPS Fix Status
fix = False

# Send to Sigfox - set to True in production
post = True

# Boolean to decide if we should wait for GPS (Testing) - set to True in production
waitForGPS = True

sleeptime = 10

sendfail = 0

# Fake Temp and Hum
fakeTemp = 20
fakeHum = 45

# Parameter Limits - for oil piantings
# https://www.artworkarchive.com/blog/how-to-store-your-art-collection-like-an-expert
tempHighest = 24
tempLowest = 18
humHighest = 50
humLowest = 40

# Print Sigfox Device ID
STR_CODE = str(binascii.hexlify(sigfox.id())).replace("'", "")[-6:].upper()
print("Stork Code:", STR_CODE)

# ------------------ FUNCTIONS ------------------
# Post all parameters to the Sigfox backend
def postData(latitude, longitude, temp, hum):
    try:
        # All Ok
        if (
            fix
            and hum >= humLowest
            and hum <= humHighest
            and temp >= tempLowest
            and temp <= tempHighest
            and not mishandle
            and sendfail < 3
        ):
            statusCode = 1
        # Stork device location unknown.
        elif (
            not fix
            and hum >= humLowest
            and hum <= humHighest
            and temp >= tempLowest
            and temp <= tempHighest
            and not mishandle
            and sendfail < 3
        ):
            statusCode = 2
        # Mishandle event detected.
        elif (
            fix
            and hum >= humLowest
            and hum <= humHighest
            and temp >= tempLowest
            and temp <= tempHighest
            and mishandle
            and sendfail < 3
        ):
            statusCode = 3
        # Temperature of the Stork at a dangerous level.
        elif (
            fix
            and temp < tempLowest
            or temp > tempHighest
            and hum >= tempLowest
            and hum <= tempHighest
            and not mishandle
            and sendfail < 3
        ):
            statusCode = 4
        # Humidity of the Stork at a dangerous level.
        elif (
            fix
            and hum < humLowest
            or hum > humHighest
            and temp >= tempLowest
            and temp <= tempHighest
            and not mishandle
            and sendfail < 3
        ):
            statusCode = 5
        # Temperature AND Humidity of the Stork at a dangerous level.
        elif (
            fix
            and hum < humLowest
            or hum > humHighest
            or temp < tempLowest
            or temp > tempHighest
            and not mishandle
            and sendfail < 3
        ):
            statusCode = 6
        # Stork device hasn't been seen in the last 30 minutes.
        elif (
            fix
            and hum >= humLowest
            and hum <= humHighest
            and temp >= tempLowest
            and temp <= tempHighest
            and not mishandle
            and sendfail >= 3
        ):
            statusCode = 7
        # Stork device location unknown & no ping in last 30 minutes.
        elif (
            not fix
            and hum >= humLowest
            and hum <= humHighest
            and temp >= tempLowest
            and temp <= tempHighest
            and not mishandle
            and sendfail >= 3
        ):
            statusCode = 8
        # Stork device location unknown & Humidity of the Stork at a dangerous level.
        elif (
            not fix
            and hum < humLowest
            or hum > humHighest
            and temp >= tempLowest
            and temp <= tempHighest
            and not mishandle
            and sendfail < 3
        ):
            statusCode = 9
        # Stork device location unknown & Temperature of the Stork at a dangerous level.
        elif (
            not fix
            and hum >= humLowest
            and hum <= humHighest
            and temp < tempLowest
            or temp > tempHighest
            and not mishandle
            and sendfail < 3
        ):
            statusCode = 10
        # Stork device location unknown & Temperature AND Humidity of the Stork at a dangerous level.
        elif (
            not fix
            and hum < humLowest
            or hum > humHighest
            and temp < tempLowest
            or temp > tempHighest
            and not mishandle
            and sendfail < 3
        ):
            statusCode = 11
        # Stork device location unknown & Mishandle event detected.
        elif (
            not fix
            and hum >= humLowest
            and hum <= humHighest
            and temp >= tempLowest
            and temp <= tempHighest
            and mishandle
            and sendfail < 3
        ):
            statusCode = 12
        # Stork device location unknown, Mishandle event detected & Stork device hasn't been seen in the last 30 minutes.
        elif (
            not fix
            and hum >= humLowest
            and hum <= humHighest
            and temp >= tempLowest
            and temp <= tempHighest
            and mishandle
            and sendfail >= 3
        ):
            statusCode = 13
        # Stork device location unknown, Mishandle event detected & Humidity of the Stork at a dangerous level.
        elif (
            not fix
            and hum < humLowest
            or hum > humHighest
            and temp >= tempLowest
            and temp <= tempHighest
            and mishandle
            and sendfail >= 3
        ):
            statusCode = 14
        # Stork device location unknown, Mishandle event detected & Temperature of the Stork at a dangerous level.
        elif (
            not fix
            and hum >= humLowest
            and hum <= humHighest
            and temp < tempLowest
            or temp > tempHighest
            and mishandle
            and sendfail >= 3
        ):
            statusCode = 15
        # Stork device location unknown, Mishandle event detected & Humidity of the Stork at a dangerous level
        # & Stork device hasn't been seen in the last 30 minutes.
        elif (
            not fix
            and hum < humLowest
            or hum > humHighest
            and temp >= tempLowest
            and temp <= tempHighest
            and mishandle
            and sendfail >= 3
        ):
            statusCode = 16
        # Stork device location unknown, Mishandle event detected & Temperature of the Stork at a dangerous level
        # & Stork device hasn't been seen in the last 30 minutes.
        elif (
            not fix
            and hum >= humLowest
            and hum <= humHighest
            and temp < tempLowest
            or temp > tempHighest
            and mishandle
            and sendfail >= 3
        ):
            statusCode = 17
        # All parameters in a DANGER state.
        elif (
            not fix
            and hum < humLowest
            or hum > humHighest
            and temp < tempLowest
            or temp > tempHighest
            and mishandle
            and sendfail >= 3
        ):
            statusCode = 18
        else:
            statusCode = 0

        pycom.heartbeat(False)
        pycom.rgbled(0x00FFFF)
        time.sleep(5)

        prg = "SENDING THE FOLLOWING DATA -> GPS: {} : {} - TEMP: {} HUM: {} STORK CODE: {}".format(
            latitude, longitude, temp, hum, statusCode
        )
        print(prg)
        longByteArray = bytearray(struct.pack("<f", float(latitude)))
        longByteArray.extend(bytearray(struct.pack("<f", float(longitude))))
        longByteArray.extend(bytearray(struct.pack("<B", temp)))
        longByteArray.extend(bytearray(struct.pack("<B", hum)))
        longByteArray.extend(bytearray(struct.pack("<B", statusCode)))
        s.send(longByteArray)
        print("DATA SENT!")
        pycom.rgbled(0x00FF00)
        time.sleep(10)
        pycom.heartbeat(True)
        print("Re-Entering Main Loop...")
        print("")
    except Exception as error:
        err = "ERROR: There was a problem posting data: {}".format(error)
        print(err)
        pass


# WAIT FOR GPS BEFORE WE START
coord = gps.coordinates()

pycom.heartbeat(False)
pycom.rgbled(0xFF7000)
time.sleep(2)
print("Locking To GPS...")
if waitForGPS and not fix:
    while coord == (None, None):
        coord = gps.coordinates()
print("GPS Position Locked!")
fix = True
pycom.rgbled(0x00FF00)

time.sleep(10)

print("")
print("Starting Main Loop:")

pycom.heartbeat(True)

# ------------------ MAIN LOOP ------------------
while True:
    lat, lng = coord

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
        print("")
    # If "sendCycle" (sendCycle is set to 10 mins normally as Sigfox allows a message to be sent every 10 minutes) mins has passed
    elif minInt >= sendCycle:
        print("{} Minutes Has Passed!".format(minInt))
        print(
            "Mishandle Counts - Warning Count: {} Danger Count: {} ".format(
                warnCount, dangerCount
            )
        )
        print("")
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

        if not lat is None and not lng is None:  # Have a GPS fix
            print("GPS Lock Acquired! - Sending Real GPS Data!")
            if post:
                pycom.heartbeat(False)
                print("Posting REAL data!")
                temp = int(str(machine.rng())[:2])
                hum = int(str(machine.rng())[:2])
                postData(lat, lng, temp, hum)
            else:
                print("postToSigfox set to False - not posting REAL data!")
        else:  # No GPS fix
            print("GPS signal lost or could not be locked - Re-locking GPS signal!")
            pycom.heartbeat(False)
            # Set LED to RED
            pycom.rgbled(0x7F0000)
            if waitForGPS and not fix:
                while coord == (None, None):
                    print("Waiting for GPS...")
                    coord = gps.coordinates()
                    print(coord)
            print("GPS position regained!")
            pycom.rgbled(0x00FFFF)
            pycom.heartbeat(True)
            fix = True
        # Set the minute counter back to zero for the next "sendCycle" min cycle
        minInt = 0
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
            # Detect a 002 mishandle (mishandles of medium severity)
            if difference > okLimit and difference < dangerLimit:
                # Increment the count of the 002 mishandles detected
                warnCount += 1
            # Detect a 003 mishandle (mishandles of high severity)
            elif difference > warningLimit:
                # Increment the count of the 002 mishandles detected
                dangerCount += 1
            else:
                pass
        # Clear the pitch and roll values for the next two that will be read in
        pitchValues.clear()
        rollValues.clear()
