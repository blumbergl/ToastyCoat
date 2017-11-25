from machine import *
import time

pin = Pin(2, Pin.OUT)

while True:
    time.sleep_ms(500)
    pin.high()  # light off
    time.sleep_ms(500)
    pin.low()  # light on