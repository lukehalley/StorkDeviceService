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

# Mishandle Boolean
mishandle = False

# Variable to track the minutes that have passed
minInt = 0

# Send every n mins
sendCycle = 10

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
    # If "sendCycle" mins has passed
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
        # Set the minute counter back to zero for the next "sendCycle" min cycle
        minInt = 0
        time.sleep(2.5)

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
