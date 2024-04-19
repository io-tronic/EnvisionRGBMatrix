# This file is executed on every boot (including wake-boot from deepsleep)

import network

import esp
esp.osdebug(None)

import gc
gc.collect()

ssid = 'envisionRGB'
password = 'envision'

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, password=password)

while ap.active() == False:
  pass

print('Connection successful')
print(ap.ifconfig())