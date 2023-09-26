import time
from rpi_lcd import LCD
from signal import signal, SIGTERM, SIGHUP, pause
from w1thermsensor import W1ThermSensor
from telee import *


sensor = W1ThermSensor()
i2c_address = 0x27
lcd = LCD()
def safe_exit(signum, frame):
    exit(1)

def read_temperature():
    try:
        temperature = sensor.get_temperature()
        return temperature
    except Exception as e:
        print("Error reading temperature:", e)
        return None

def display_lcd(): 
    lcd(line1, line2)
    lcd.set(line1, 1)
    lcd.set(line2, 2)

try:
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)
    while True:
        temperature = read_temperature()
        if temperature is not None:
            line1 = "suhu air: {:.2f} C".format(temperature)
            line2 = ("Lanjutkan minum!")
            display_lcd()
        time.sleep (1)

        if temperature is not None:
            send_telegram(line1)
            send_telegram(line2)
        time.sleep(5)  # Delay 1 second
        
except KeyboardInterrupt:
    lcd.lcd_clear()
    GPIO.cleanup()
    print("Exiting...")
