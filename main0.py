from network import WLAN
import machine
from machine import Timer
import time
try:
    import urequests as requests
except ImportError:
    import requests


wlan = WLAN(mode=WLAN.STA)

nets = wlan.scan()
for net in nets:
    if net.ssid == 'woof':
        print('Network found!')
        wlan.connect(net.ssid, auth=(net.sec, 'cafebabeca'), timeout=5000)
        while not wlan.isconnected():
            machine.idle() # save power while waiting
        print('WLAN connection succeeded!')
        break

print(wlan.ifconfig())

led=machine.Pin("G16",machine.Pin.OUT)
button=machine.Pin("G17",machine.Pin.IN, pull=machine.Pin.PULL_UP)

def handler(button):
    irq.disable()
    time.sleep(1)
    led.toggle()
    irq.enable()

#irq=button.callback(machine.Pin.IRQ_FALLING, handler)

count=0
down=False
up=False
# send some bytes
#s.send(bytes([0x01, 0x02, 0x03]))

def wait_pin_change(pin,state):
    # wait for pin to change value
    # it needs to be stable for a continuous 20ms
    cur_value = pin.value()
    pressed = 0
    while pressed < 20:
        if  pin.value()==state:
            pressed += 1
        else:
            pressed = 0
        time.sleep_ms(1)

while True:
    wait_pin_change(button,0)
    wait_pin_change(button,1)
    led.toggle()
    #s.send(bytes([0x01, 0x02, 0x03]))
    print("send")

    count=count+1
    if count%2==0:
        status="off"
    else:
        status="on"
    print(count)
    requests.request("POST","http://homepi:3000/profiles/standard",'{"status":"'+status+'"}',None,{"Content-Type" : "application/json"}).text
