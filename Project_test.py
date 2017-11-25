from machine import *
import time

# initiate all the pins
adc = ADC(0)

heat = Pin(5, Pin.OUT)
heat.value(0)

pressure1 = Pin(16, Pin.OUT)
pressure1.value(0)

pressure2 = Pin(0, Pin.OUT)
pressure2.value(0)

temp1 = Pin(2, Pin.OUT)
temp1.value(0)

temp2 = Pin(15, Pin.OUT)
temp2.value(0)

# Code that reads values for analog devices (turns on, reads, and off the relevant digital pin)
def get_analog_value(pin):
    pin.value(1)
    time.sleep_ms(10)
    v = adc.read()
    time.sleep_ms(10)
    pin.value(0)
    return v

# run this program on loop
while True:
    time.sleep_ms(750)
    
    # Get Values
    p1 = get_analog_value(pressure1)
    p2 = get_analog_value(pressure2)
    t1 = get_analog_value(temp1)
    t2 = get_analog_value(temp2)

    print(p1, p2, t1, t2)
    
    # adjust heating (currently LED)
    if t1 < 60: # Value from testing
        heat.value(1)
    else:
        heat.value(0)
    if p1 > 500 and p2 > 500:
        heat.value(1)
