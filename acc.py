# Imports
import time
from LIS2HH12 import LIS2HH12
from pytrack import Pytrack
import time
import gc

# Init of the Pytrack sensors
py = Pytrack()
acc = LIS2HH12()

# Array to collect two pitch and roll values to compare
pitchValues = []
rollValues = []

# Init the timer
init_timer = time.time()

# Setting the mishandle limits
okLimit = 30
warningLimit = 55
dangerLimit = 100

# Mishandle Counts
warnCount = 0
dangerCount = 0

while True:
    final_timer = time.time()
    diff = final_timer - init_timer
    if diff >= 60:
        init_timer = time.time()
        print("One Minute Passed!")
        print(
            "Mishandle Counts - Warning Count: {} Danger Count: {} ".format(
                warnCount, dangerCount
            )
        )
        time.sleep(10)
    elif diff >= 900:
        print("15 Minutes Passed!")
        print(
            "Mishandle Counts - Warning Count: {} Danger Count: {} ".format(
                warnCount, dangerCount
            )
        )
        time.sleep(10)
    else:
        while len(pitchValues) <= 1 and len(rollValues) <= 1:
            pitchValues.append(acc.pitch())
            rollValues.append(acc.roll())
        else:
            diff = abs(pitchValues[1] - pitchValues[0]) + abs(
                rollValues[1] - rollValues[0]
            )
            print("Diff: {}".format(diff))
            if diff > okLimit and diff < dangerLimit:
                print("Mishandle Warning: 002")
                warnCount += 1
                time.sleep(1)
            elif diff > warningLimit:
                dangerCount += 1
                print("Mishandle Danger: 003")
                time.sleep(1)
            else:
                pass
        pitchValues.clear()
        rollValues.clear()
