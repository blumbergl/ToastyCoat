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


def http_get(url):
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    #print("host = " + host)
    #print("path = " + path)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    data_str = ''
    while True:
        data = s.recv(100)
        if data:
            #print("new iteration")
            #print(str(data, 'utf8'), end='')
            data_str += str(data, 'utf8')
        else:
            break
    s.close()
    return data_str

# Code that reads values for analog devices (turns on, reads, and off the relevant digital pin)
def get_analog_value(pin):
    pin.value(1)
    time.sleep_ms(10)
    v = adc.read()
    time.sleep_ms(10)
    pin.value(0)
    return v
'''
def on_subscribe(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
  # reconnect then subscriptions will be renewed.
  client.subscribe("$SYS/#")
'''
def on_subscribe(client, userdata, mid, granted_qos):
  print("Subscribed!")
#
# connect ESP8266 to Thingspeak using MQTT
#
myMqttClient = "cmorganti"  # can be anything unique
thingspeakIoUrl = "mqtt.thingspeak.com" 
c = MQTTClient(myMqttClient, thingspeakIoUrl, 1883)  # uses unsecure TCP connection
#c.set_callback(on_subscribe)
c.connect()



def fahrenheit_to_celsius(temp):
  c_temp = (float(temp) - 32.0)*5.0/9.0
  return c_temp

#
# publish temperature and free heap to Thingspeak using MQTT
#
def load_from_config():
  f_input = open('web.config', 'r').read()
  settings = json.loads(f_input)
  return settings

settings = load_from_config()
i2cDeviceAddress = 24
i2cRegisterAddress = 5
i2cNumBytesToRead = 2
thingspeak_sensor_channel_id= settings['thingspeak_sensor_channel_id']  
thingspeak_sensor_write_key = settings['thingspeak_sensor_write_key']
publishPeriodInSec = 2
PRESSURE_THRESHOLD = 500
TEMP_STEPSIZE = 5.0

# TODO add read/write credentials for thingspeak preferences channel
thingspeak_prefs_channel_id = settings['thingspeak_prefs_channel_id'] 
thingspeak_prefs_write_key = settings['thingspeak_prefs_write_key'] 
thingspeak_prefs_read_key = settings['thingspeak_prefs_read_key'] 

def update_pressure_with_gestures(preferred_temp):
  if (p1 + p2)/2.0 > PRESSURE_THRESHOLD:
    preferred_temp += TEMP_STEPSIZE
  return preferred_temp


def control_heating(t1, t2, preferred_temp, unzipped):
  if (t1 + t2)/2.0 > preferred_temp:
    # TODO turn off heating
    heat.value(0)
  elif unzipped:
    heat.value(0)
    preferred_temp -= TEMP_STEPSIZE
  else:
    heat.value(1)

# TODO what to do when conflicting "gestures" -- jacket unzipped AND pressure sensors activated 
## possible solution -- only heat when jacket is zipped?

while True:

  # Get sensor values
  p1 = get_analog_value(pressure1)
  p2 = get_analog_value(pressure2)
  t1 = get_analog_value(temp1)
  t2 = get_analog_value(temp2)
  t1_c = t1#fahrenheit_to_celsius(t1)
  t2_c = t2 #fahrenheit_to_celsius(t2) 

  # see if gestures are on from thingspeak
  http_resp = http_get("https://api.thingspeak.com/channels/" + thingspeak_prefs_channel_id + "/fields/2.json?api_key=" + thingspeak_prefs_read_key + "&results=1")
  gestures_on = bool(json.loads(http_resp.split('\r\n\r\n')[1])['feeds'][0]['field2'])
  # print(gestures_on)

  # get preferred temperature from thingspeak
  http_resp = http_get("https://api.thingspeak.com/channels/" + thingspeak_prefs_channel_id + "/fields/1.json?api_key=" + thingspeak_prefs_read_key + "&results=1")
  last_preferred_temp = float(json.loads(http_resp.split('\r\n\r\n')[1])['feeds'][0]['field1'])
  # print(last_preferred_temp)
  preferred_temp = last_preferred_temp
  preferred_temp = 90

  # update preferred temperature using gestures 
  if gestures_on:
    preferred_temp = update_pressure_with_gestures(preferred_temp)

  # TODO get if jacket is unzipped
  unzipped = False
 
  # control heating element accordingly
  control_heating(t1, t2, preferred_temp, unzipped)

  # publish sensor data to thingspeak sensor channel
  credentials = "channels/{:s}/publish/{:s}".format(thingspeak_sensor_channel_id, thingspeak_sensor_write_key)  
  payload = "field1={:.1f}&field2={:.1f}&field3={:.1f}&field4={:.1f}&field5={:.1f}&field6={:.1f}\n".format(t1, t2, t1_c, t2_c, p1, p2)
  c.publish(credentials, payload)

  # if temperature preference has changed from user gestures, update thingspeak preferences channel
  if preferred_temp != last_preferred_temp:
    credentials = "channels/{:s}/publish/{:s}".format(thingspeak_prefs_channel_id, thingspeak_prefs_write_key)  
    payload = "field1={:.1f}&field2={:s}\n".format(preferred_temp, str(gestures_on))
    c.publish(credentials, payload)
  
  time.sleep(5)
  print("done sleeping")
  
c.disconnect() 