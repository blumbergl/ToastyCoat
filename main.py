# MQTT Micropython code adapted from https://github.com/MikeTeachman/micropython-thingspeak-mqtt-esp8266/blob/master/mqtt-to-thingspeak.py
#     
import dht
from machine import *
#import socket
import network
import time
import gc
from umqtt.simple import MQTTClient
import ujson as json
import socket



"""
Connect to MIT wifi 
Adapted from https://docs.micropython.org/en/latest/esp8266/esp8266/tutorial/network_basics.html
"""
def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('MIT', '')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())



"""
Method for HTTP GET requests
From https://docs.micropython.org/en/latest/esp8266/esp8266/tutorial/network_tcp.html
"""
def http_get(url):
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    data_str = ''
    while True:
        data = s.recv(100)
        if data:
            data_str += str(data, 'utf8')
        else:
            break
    s.close()
    return data_str


"""
Read values for analog devices (turns on, reads, and off the relevant digital pin)
"""
def get_analog_value(pin):
    pin.value(1)
    time.sleep_ms(10)
    v = adc.read()
    time.sleep_ms(10)
    pin.value(0)
    return v

"""
Convert Fahrenheit to Celsius
"""
def fahrenheit_to_celsius(temp):
  c_temp = (float(temp) - 32.0)*5.0/9.0
  return c_temp

"""
Load API keys, etc.
"""
def load_from_config():
  f_input = open('web.config', 'r').read()
  settings = json.loads(f_input)
  return settings

"""
Update temperature preferences if pressure sensor results above threshold and 
jacket is zipped.
"""
def update_pressure_with_gestures(preferred_temp, unzipped):
  if not unzipped and (p1 + p2)/2.0 >= PRESSURE_THRESHOLD:
    #print("pressure increasing preferred temp")
    preferred_temp = min(preferred_temp + TEMP_STEPSIZE, TEMP_MAX)
  elif unzipped:
    #print("unzipped, will try to decrease preferred temp")
    preferred_temp = max(preferred_temp - TEMP_STEPSIZE, TEMP_MIN)
  #print ("preferred temp now " + str(preferred_temp))
  return preferred_temp


"""
After user gestures have been detected or not, current jacket temperature detected, zipper status determined, and user input from web app determined, 
control heating accordingly
"""
def control_heating(t1, t2, preferred_temp, unzipped):
  if (t1 + t2)/2.0 > preferred_temp:
    # turn off heating
    heat.value(0)
  # also don't heat if jacket is unzipped
  elif unzipped:
    heat.value(0)
  else:
    heat.value(1)

"""
Scale the temperature sensor result to a better "coziness" setting
"""
def scale_temp_sensor_result(x):
  base = 55
  step_size = 4
  return min(max(TEMP_MIN, int((x - base)/step_size)), TEMP_MAX)



# initiate all the pins on the microcontroller

adc = ADC(0)

# heating activation
heat = Pin(5, Pin.OUT)
heat.value(0)

# pressure sensors
pressure1 = Pin(16, Pin.OUT)
pressure1.value(0)

pressure2 = Pin(0, Pin.OUT)
pressure2.value(0)

# temperature sensors
temp1 = Pin(2, Pin.OUT)
temp1.value(0)

temp2 = Pin(15, Pin.OUT)
temp2.value(0)

# zipper sensor (unzipped = 1, zipped = 0)
zipper = Pin(13, Pin.IN)


# get API key values, etc.
settings = load_from_config()
# delay between getting sensor values
publishPeriodInSec = 10
# minimum threshold for pressure sensor gestures
PRESSURE_THRESHOLD = 150
# how much to increase/decrease preferred temp due to user gestures
TEMP_STEPSIZE = 1.0
TEMP_MIN = 1
TEMP_MAX = 10

# write credentials for thingspeak sensor channel
thingspeak_sensor_channel_id= settings['thingspeak_sensor_channel_id']  
thingspeak_sensor_write_key = settings['thingspeak_sensor_write_key']
# read/write credentials for thingspeak preferences channel
thingspeak_prefs_channel_id = settings['thingspeak_prefs_channel_id'] 
thingspeak_prefs_write_key = settings['thingspeak_prefs_write_key'] 
thingspeak_prefs_read_key = settings['thingspeak_prefs_read_key'] 

# connect to wifi
do_connect()

# connect ESP8266 to Thingspeak using MQTT
myMqttClient = "cmorganti"  
thingspeakIoUrl = "mqtt.thingspeak.com" 
c = MQTTClient(myMqttClient, thingspeakIoUrl, 1883)  
c.connect()



while True:

  # Get sensor values
  p1 = get_analog_value(pressure1)
  p2 = get_analog_value(pressure2)
  t1 = scale_temp_sensor_result(get_analog_value(temp1))
  t2 = scale_temp_sensor_result(get_analog_value(temp2))
  t1_c = fahrenheit_to_celsius(t1)
  t2_c = fahrenheit_to_celsius(t2) 

  # see if gestures are on from thingspeak
  http_resp = http_get("https://api.thingspeak.com/channels/" + thingspeak_prefs_channel_id + "/fields/2.json?api_key=" + thingspeak_prefs_read_key + "&results=1")
  gestures_on = json.loads(http_resp.split('\r\n\r\n')[1])['feeds'][0]['field2']
  
  # Dealing with inconsistencies in how web app and microcontroller record gestures being on/off # TODO fix this
  if gestures_on == "true":
    gestures_on = True
  elif gestures_on[0] == "1":
    gestures_on = True
  else:
    gestures_on = False

  # get if jacket is unzipped
  unzipped = zipper.value()

  # get preferred temperature from thingspeak
  http_resp = http_get("https://api.thingspeak.com/channels/" + thingspeak_prefs_channel_id + "/fields/1.json?api_key=" + thingspeak_prefs_read_key + "&results=1")
  try:
    last_preferred_temp = float(json.loads(http_resp.split('\r\n\r\n')[1])['feeds'][0]['field1'])
  except:
    last_preferred_temp = 5.0
    # TODO having issues when last Thingspeak value is null 
    print("last preferred temp from thingspeak is null")


  preferred_temp = last_preferred_temp

  # update preferred temperature using gestures 
  if gestures_on:
    preferred_temp = update_pressure_with_gestures(preferred_temp, unzipped)
    gestures_on = True
  else:
    gestures_on = False

 
  # control heating element accordingly
  control_heating(t1, t2, preferred_temp, unzipped)

  # publish sensor data to thingspeak sensor channel
  credentials = "channels/{:s}/publish/{:s}".format(thingspeak_sensor_channel_id, thingspeak_sensor_write_key)  
  payload = "field1={:.1f}&field2={:.1f}&field3={:.1f}&field4={:.1f}&field5={:.1f}&field6={:.1f}&field7={:.1f}\n".format(t1, t2, t1_c, t2_c, p1, p2, float(unzipped))
  c.publish(credentials, payload)

  # if temperature preference has changed from user gestures, update thingspeak preferences channel
  if preferred_temp != last_preferred_temp and gestures_on:
    credentials = "channels/{:s}/publish/{:s}".format(thingspeak_prefs_channel_id, thingspeak_prefs_write_key)  
    payload = "field1={:.1f}&field2={:f}\n".format(preferred_temp, float(gestures_on))
    c.publish(credentials, payload)
    print ("published updated preferences")
  
  last_zipper_val = unzipped
  time.sleep(publishPeriodInSec)

  
c.disconnect() 
