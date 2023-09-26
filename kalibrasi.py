import RPi.GPIO as GPIO
from hx711 import HX711

GPIO.setmode(GPIO.BCM)

hx = HX711(dout_pin=18, pd_sck_pin=17)

hx.zero()

input('Place know weight on scale & press Enter: ')
reading = hx.get_data_mean(readings=30)

known_weight_grams = input('Enter the known weight in grams & press Enter: ')
value = float(known_weight_grams)

ratio = reading/value
hx.set_scale_ratio(ratio)

while True:
    weight = hx.get_weight_mean(30)
    print (weight, "g")

                            
