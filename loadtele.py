import time
import sys
import smbus
from RPi_GPIO_i2c_LCD import lcd
from telee import *
from w1thermsensor import W1ThermSensor

GPIO.setmode(GPIO.BCM)
buzzer = 23
GPIO.setup(buzzer,GPIO.OUT)
bus = smbus.SMBus(1)


sensor = W1ThermSensor()
EMULATE_HX711=False
i2c_address = 0x27
tampilan = lcd.HD44780(i2c_address)
time.sleep(1)

referenceUnit = 1

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711


hx = HX711(18, 17)

hx.set_reading_format("MSB", "MSB")

hx.set_reference_unit(-513)

hx.reset()

hx.tare()

print("Tare done! Add weight now...")

def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print("Bye!")
    sys.exit()

#def reset_weight():
 #   "Fungsi untuk me-reset berat"
  #  hx.reset()
   # hx.tare()
    #print("Tare done! Add weight now...")

#def print_to_lcd(line1, line2):
def lcdDisplay(line1, line2):
    tampilan.clear()
    time.sleep(0.5)
    tampilan.set(line1, 1) #ubah namanya
    time.sleep(0.5)
    tampilan.set(line2, 2)
    time.sleep(0.5)

def read_temperature():
    try:
        temperature = sensor.get_temperature()
        return temperature
    except Exception as e:
        print("Error reading temperature:", e)
        return None


def alarm():
    for i in range(1):
        GPIO.output(buzzer,GPIO.HIGH)
        time.sleep(10)
        GPIO.output(buzzer,GPIO.LOW)


def main():
    # set nilai awal
    check_count = 0
    # air yg harus diminum selama 2 jam adalah 200ml (225 botol + 200 air)
    water_to_drink = 100
    # total air yg sudah diminum selama 2 jam
    drunk_water = 0

    try:
        # 1. Inisiasi berat awal
        previous_weight = hx.get_weight()
        tampilan.set (previous_weight, 1) 
        time.sleep(5)
        while True:
            temperature = read_temperature()
            current_weight = hx.get_weight()
            delta_weight = previous_weight - current_weight
            print ("suhu air : ", temperature)
            print("Current weight : ", current_weight)
            print("delta weight:", delta_weight)
	    
            # cek masih dalam waktu 2 jam tiap 30 menit
            if current_weight > 3:

                if check_count > 0:
                # reset ke nilai awal
                    check_count = 0
                    drunk_water = 0
                check_count += 1

            # 2. Cek berat tiap sekian menit
                #current_weight = hx.get_weight()
                #delta_weight = previous_weight - current_weight 
            
                # Cek untuk refill
                berat_botol = 254
                if current_weight == berat_botol:
                    print("Ayo refill botolnya!")
                    line1 = ("Ayo refill botolnya!")
                    send_telegram(line1)
                    tampilan.set(line1, 1)
                    time.sleep(50)
            

            
                else:
                # simpan selisih minum ke drunk water untuk mengetahui total yg sudah diminum selama 2 jam
                    drunk_water += delta_weight

                # cek air yg sudah diminum dibandingkan dengan air yg harus dinimum selama 2 jam
                # jika selisih beban diatas 400 ml maka bagus sudah minum
                # berat botol = 225 gr
                    if drunk_water < water_to_drink:
                        print("Saatnya minum 200 ml air!")
                        line1 = ("Saatnya minum")
                        minum = ("200 ml air")
                        notif = ("Saatnya minum 200 ml air!")
                        alarm()
                        send_telegram(notif)
                        tampilan.set(line1, 1)
                        tampilan.set(minum,2)
                        time.sleep(10)
                    else:
                        print("Bagus! Anda sudah minum 200 ml dalam 2 jam ini, Lanjutkan!!")
                        tele = ("Bagus! Anda sudah minum 200 ml dalam 2 jam ini, Lanjutkan!!")
                        line1 = ("Bagus!Anda sudah")
                        line2 = ("minum 200 ml air")
                        send_telegram(tele)
                        tampilan.set(line1,1)
                        tampilan.set(line2,2)
                        time.sleep(10)
                    check_count += 1
                    previous_weight = current_weight
            
            #beban_penuh = 45
            #if current_weight >= beban_penuh:
             #   check_count > 6
              #  print ("air telah direfill", current_weight)
            # sleep tiap 30 menit
                
            else:
                print("tidak ada beban")
            
    except (KeyboardInterrupt, SystemExit):
        print("Membaca beban selesai.")

    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
