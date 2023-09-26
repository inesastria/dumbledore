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
def lcdDisplay(text, line):
    #time.sleep(0.5)
    tampilan.set(text, line) #ubah namanya

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
        time.sleep(5)
        GPIO.output(buzzer,GPIO.LOW)


def main():
    # set nilai awal
    # durasi untuk pengecekan apakah sudah minum tiap sekian menit dalam 2 jam
    duration = 1
    # durasi untuk pengecekan setiap 2 jam
    duration_notification = 10

    # inisiasi waktu mulai
    start = time.time()
    start_notification = start

    # state untuk notifikasi jika sudah minum, untuk mencegah notifikasi berkali kali
    good_notification_sent = False

    # air yg harus diminum selama 2 jam adalah 200ml (225 botol + 200 air)
    water_to_drink = 100
    # total air yg sudah diminum selama 2 jam
    drunk_water = 0

    try:
        # 1. Inisiasi berat awal

        previous_weight = hx.get_weight()
        while True:
            # dapatkan waktu sekarang
            time_now = time.time()    
            
            # hitung waktu yg sudah berjalan dari start
            elapsed_time = time_now - start # pengecekan apakah sudah cukup minum dalam tiap sekian menit dalam 2 jam
            elapsed_time_notification = time_now - start_notification # pengecekan untuk kirim notifikasi setiap 2 jam
            
            temperature = read_temperature()
            current_weight = hx.get_weight()
            
            delta_weight = previous_weight - current_weight
            
            print (f"suhu air : {temperature:.2f}")
            print(f"Current weight : {current_weight:.2f}")
            print(f"delta weight: {delta_weight:.2f}")
            tampilan.clear()
            lcdDisplay("berat air kamu: ", 1)
            lcdDisplay(f"{previous_weight:.2f}", 2)
            time.sleep(3)

            # cek masih dalam waktu 2 jam tiap 30 menit
            if current_weight > 0:
            # 2. Cek berat tiap sekian menit
                #current_weight = hx.get_weight()
                #delta_weight = previous_weight - current_weight 
            
                # Cek untuk refill
                berat_botol = 254
                if current_weight == berat_botol:
                    print("Ayo refill botolnya!")
                    line1 = ("Ayo refill botolnya!")
                    send_telegram(line1)
                    tampilan.clear()
                    lcdDisplay(line1, 1)
                else:
                # simpan selisih minum ke drunk water untuk mengetahui total yg sudah diminum selama 2 jam
                    drunk_water += delta_weight

                # cek air yg sudah diminum dibandingkan dengan air yg harus dinimum selama 2 jam
                # jika selisih beban diatas 400 ml maka bagus sudah minum
                # berat botol = 225 gr
                    if elapsed_time >= duration:
                        start = time_now
                        if drunk_water >= water_to_drink:
                            print("Bagus! Anda sudah minum 200 ml dalam 2 jam ini, Lanjutkan!!")
                            tele = ("Bagus! Anda sudah minum 200 ml dalam 2 jam ini, Lanjutkan!!")
                            line1 = ("Bagus!Anda sudah")
                            line2 = ("minum 200 ml air")
                            tampilan.clear()
                            lcdDisplay("berat air kamu: ", 1)
                            lcdDisplay(f"{previous_weight:.2f}", 2)

                            if not good_notification_sent:
                                # ubah state kirim notifikasi sudah berhasil
                                send_telegram(tele)
                                good_notification_sent = True

                    if elapsed_time_notification >= duration_notification:
                        start_notification = time_now
                        if drunk_water < water_to_drink:
                            print("Saatnya minum 200 ml air!")
                            line1 = ("Saatnya minum")
                            minum = ("200 ml air")
                            notif = ("Saatnya minum 200 ml air!")
                            alarm()
                            send_telegram(notif)
                            tampilan.clear()
                            lcdDisplay(line1, 1)
                            lcdDisplay(minum,2)
                            
                        else:
                            print("Bagus! Anda sudah minum 200 ml dalam 2 jam ini, Lanjutkan!!")
                            tele = ("Bagus! Anda sudah minum 200 ml dalam 2 jam ini, Lanjutkan!!")
                            line1 = ("Bagus!Anda sudah")
                            line2 = ("minum 200 ml air")
                            send_telegram(tele)
                            tampilan.clear()
                            lcdDisplay(line1,1)
                            lcdDisplay(line2,2)

                        # Reset count
                        drunk_water = 0
                        good_notification_sent = False


                    previous_weight = current_weight
            
            #beban_penuh = 45
            #if current_weight >= beban_penuh:
             #   check_count > 6
              #  print ("air telah direfill", current_weight)
            # sleep tiap 30 menit
                
            else:
                print("tidak ada beban")
                lcdDisplay ("tidak ada beban", 1)
            
            time.sleep(1)
            
    except (KeyboardInterrupt, SystemExit):
        print("Membaca beban selesai.")

    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
