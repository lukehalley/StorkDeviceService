import time
from LIS2HH12 import LIS2HH12
from pytrack import Pytrack
import time
import gc

py = Pytrack()
acc = LIS2HH12()

pitchValues = []
rollValues = []

init_timer = time.time()

while True:
    final_timer = time.time()
    diff = final_timer - init_timer
    pitch = acc.pitch()
    roll = acc.roll()
    if diff > 60:
        init_timer = time.time()
        print("One Minute Passed!")
        time.sleep(5)
    else:
        while len(pitchValues) <= 1 and len(rollValues) <= 1:
            pitchValues.append(acc.pitch())
            rollValues.append(acc.roll())
        print("2 Values In -> {},{}".format(pitchValues, rollValues))
        pitchValues.clear()
        rollValues.clear()
        time.sleep(1)
