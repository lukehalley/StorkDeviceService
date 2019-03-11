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
        print("One Minute Passed! Data -> {},{}".format(pitchValues, rollValues))
        time.sleep(30)
    else:
        pitchValues.append(acc.pitch())
        rollValues.append(acc.roll())
        print("Diff: {} - Mem: {}".format(diff, gc.mem_free()))
        time.sleep(1)
