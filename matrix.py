import time

from ws2801 import WS2801Pixels

from machine import Pin
from machine import SPI

xres = const(27)
yres = const(24)
ledSPI = SPI(1, 1000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
frameBytes = xres * yres * 3
lineBytes = xres * 3

wall = WS2801Pixels(xres * yres, ledSPI)  # neopixel.NeoPixel(machine.Pin(pin), xres * yres)
wall.set_pixels_rgb(30,0,0)
wall.show()

@micropython.viper
def zickzack_rgb24(fbuf):
    buf = ptr8(fbuf)
    for y in range(1, yres, 2):
        offset_s = xres * y * 3
        offset_e = offset_s + 3 * (xres - 1)
        # print("{} - {}".format(offset_s, offset_e))
        for x in range(0, xres//2):
            tmp = buf[offset_e - x * 3] 
            buf[offset_e - x * 3] =  buf[offset_s + x * 3]
            buf[offset_s + x * 3] = tmp
            tmp = buf[offset_e - x * 3 +1] 
            buf[offset_e-x * 3 + 1] =  buf[offset_s + x * 3 +1]
            buf[offset_s+x * 3 + 1] = tmp
            tmp = buf[offset_e - x * 3 +2] 
            buf[offset_e - x * 3 + 2] =  buf[offset_s + x * 3 + 2]
            buf[offset_s+x * 3 + 2] = tmp
            

def set_leds(buf):
    zickzack_rgb24(buf)
    ledSPI.write(buf)
    time.sleep(0.002)
    
