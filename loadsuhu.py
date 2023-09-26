#! /usr/bin/python2

import os
import glob
import time
import sys
import requests
from telee import *


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c


EMULATE_HX711 = False

UBIDOTS_TOKEN = "BBFF-0hf5U3LFdeXCYmXxqqCIlgzRfeIbvs"
UBIDOTS_DEVICE_LABEL = "ds18b20"
UBIDOTS_TEMPERATURE_VARIABLE_LABEL = "suhu-air-saat-ini"
UBIDOTS_WEIGHT_VARIABLE_LABEL = "berat"

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()

    print("Bye!")
    sys.exit()

hx = HX711(18, 17)

hx.set_reading_format("MSB", "MSB")

hx.set_reference_unit(-513)

hx.reset()

hx.tare()

print("Tare done! Add weight now...")

line1 =("Saatnya minum 200 ml air!")

send_telegram(line1) 
time.sleep (10)

while True:
    try:
        temperature = read_temp()
        weight = hx.get_weight(5)
        print(f"Temperature: {temperature:.2f} C, Weight: {weight:.2f}")
        

        
        temperature_payload = {UBIDOTS_TEMPERATURE_VARIABLE_LABEL: temperature}
        temperature_headers = {"X-Auth-Token": UBIDOTS_TOKEN}
        temperature_url = f"https://industrial.api.ubidots.com/api/v1.6/devices/{UBIDOTS_DEVICE_LABEL}"
        temperature_response = requests.post(temperature_url, json=temperature_payload, headers=temperature_headers)

        
        weight_payload = {UBIDOTS_WEIGHT_VARIABLE_LABEL: weight}
        weight_headers = {"X-Auth-Token": UBIDOTS_TOKEN}
        weight_url = f"https://industrial.api.ubidots.com/api/v1.6/devices/{UBIDOTS_DEVICE_LABEL}"
        weight_response = requests.post(weight_url, json=weight_payload, headers=weight_headers)

        print(f"Data dikirim ke Ubidots. Temperature: {temperature_response.text}, Weight: {weight_response.text}")

        hx.power_down()
        hx.power_up()
        time.sleep(1)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
