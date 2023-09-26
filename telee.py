import telepot
import RPi.GPIO as GPIO
import time
import datetime

def send_telegram(message):
	bot = telepot.Bot('6363584432:AAFZR_ubpYGJGUrhyZ1d-IxYi8capByOY4Y')
	chat_id = '1282727324'
	bot.sendMessage(chat_id,message)