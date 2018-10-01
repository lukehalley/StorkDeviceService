from network import WLAN
wlan = WLAN(mode=WLAN.STA)
import machine

nets = wlan.scan()
for net in nets:
    if net.ssid == 'IoT2':
        print('Network found!')
        wlan.connect(net.ssid, auth=(net.sec, 'ilikecake'), timeout=5000)
        while not wlan.isconnected():
            machine.idle() # save power while waiting
        print('WLAN connection succeeded!')
        break
