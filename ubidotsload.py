#! /usr/bin/python2

import time
import sys
import requests


EMULATE_HX711 = False

referenceUnit = 1

UBIDOTS_TOKEN = "BBFF-uiRoEcNQQGUvTqNOKIuAdKFLkBtpza"
UBIDOTS_DEVICE_LABEL = "lodsel"
UBIDOTS_VARIABLE_LABEL_1 = "beban"

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

hx.set_reference_unit(-521)

hx.reset()

hx.tare()

print("Tare done! Add weight now...")



while True:
    try:
        val = hx.get_weight(5)
        print(val)
        # Mengirim data berat ke Ubidots
        payload = {UBIDOTS_VARIABLE_LABEL_1: val}
        headers = {"X-Auth-Token": UBIDOTS_TOKEN}
        url = f"https://industrial.api.ubidots.com/api/v1.6/devices/{UBIDOTS_DEVICE_LABEL}"
        response = requests.post(url, json=payload, headers=headers)

        print(f"Data sent to Ubidots. Response: {response.text}")

        hx.power_down()
        hx.power_up()
        time.sleep(0.1)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
