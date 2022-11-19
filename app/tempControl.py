#sudo apt install Adafruit-DHT RPi.GPIO
# pip3 install ephem

import Adafruit_DHT
import RPi.GPIO as GPIO
import time, datetime
import configparser
# import telegram_client # deprecated
import ephem
from dotenv import dotenv_values
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


config = dotenv_values("../environment/allsky.env")
INFLUX_TOKEN = config['INFLUX_TOKEN']
INFLUX_ORG = config['INFLUX_ORG']
INFLUX_BUCKET = config['INFLUX_BUCKET']
INFLUX_URL = config['INFLUX_URL']
device_lat = config['device_lat']
device_lng = config['device_lng']
# TELEGRAM_TOKEN = config['TELEGRAM_TOKEN']
# TELEGRAM_TO = config['TELEGRAM_TO']

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN)
write_api = client.write_api(write_options=SYNCHRONOUS)


config = configparser.ConfigParser()
cfgFile = './config.cfg'
config.read(cfgFile)
sections = config.sections()

#read Values from config
alarmMaxTemp = int(config['telegram']['alarmMaxTemp'])
alarmMinTemp = int(config['telegram']['alarmMinTemp'])

sensortype = int(config['tempControl']['sensortype'])
sensorpin = int(config['tempControl']['sensorpin'])
fanpin = int(config['tempControl']['fanpin'])
fanONtemp = int(config['tempControl']['fanONtemp'])
fanOFFtemp = int(config['tempControl']['fanOFFtemp'])

ledpin = int(config['default']['ledpin'])
templatefile = config['default']['templatefile']
indexfile = config['default']['indexfile']
datafile = config['default']['datafile']
logpath = config['default']['logpath']

GPIO.setmode(GPIO.BCM)
GPIO.setup(fanpin, GPIO.OUT)
GPIO.setup(ledpin, GPIO.OUT)


def flogger(txt):
   f = open(logpath, mode='a', encoding='utf-8')
   f.write(str(txt) + '\n')
   f.close

def day_or_night():

   obs = ephem.Observer()
   obs.pressure = 1000
   obs.elevation = 156
   obs.lat = device_lat
   obs.lon = device_lng
   obs.date = datetime.datetime.today() - datetime.timedelta(hours=1, minutes=0)

   sun = ephem.Sun()
   sun.compute(obs)
   sun_angle = float(sun.alt) * 57.2957795 # Convert Radians to degrees
   print(f'sun angle to horizon={sun_angle}')

   # alth, altm, _ = str(sun.alt).split(':')
   # alth = int(alth)
   # altm = int(altm)
   # alt = alth - round(1 / (60 / altm),2)

   if sun_angle < 0.0:
      sun_status = "night"
   else:
      sun_status = "day"

   return(sun_status)


def loop():
    now = datetime.datetime.now()
    fan = 'OFF'
    iFan = 0

    #while True:
    # Sensortype DHT11=11, DHT22=22
    humi, temp = Adafruit_DHT.read_retry(sensortype, sensorpin)
    humi, temp = round(humi,1), round(temp,1)
    print(humi, temp)
    flogger(f'temp={temp}, humi={humi}')

    # # Temperatur Alarm
    if temp >= alarmMaxTemp:
        pass
        # telegram_client.sendTxtMsg(TELEGRAM_TOKEN,TELEGRAM_TO,f'Temperature alarm: In the dome are' + str(temp) + 'degree celsius.')

    if temp < alarmMinTemp:
        pass
        # telegram_client.sendTxtMsg(TELEGRAM_TOKEN,TELEGRAM_TO,f'Temperature alarm deescalation: In the dome are {temp} degree celsius.')

    if type(temp) is not float:
        temp = 0.0

    if type(humi) is not float:
        humi = 0.0

    # Temperature control - is temperature over value x, enable fan.
    if temp >= fanONtemp:
        GPIO.output(fanpin, GPIO.HIGH)
        fan = 'ON'
        iFan = 1

    if temp < fanOFFtemp:
        GPIO.output(fanpin, GPIO.LOW)
        fan = 'OFF'
        iFan = 0

    flogger(f'fan={fan}, iFan={iFan}')
    dn = day_or_night()
    flogger(f'DayOrNight={dn}')
    if dn == 'night':
        GPIO.output(ledpin, GPIO.HIGH)
    else:
        GPIO.output(ledpin, GPIO.LOW)


    f = open(templatefile,mode='r',encoding='utf-8')
    html = f.read()
    f.close

    html = html.replace('%temp%',str(temp))
    html = html.replace('%humi%',str(humi))
    html = html.replace('%fan%',str(fan))
    html = html.replace('%ts%',str(now))

    f = open(indexfile,mode='w',encoding='utf-8')
    f.write(html)
    f.close

    now = str(now).split('.')[0]
    data = f'{temp},{humi},{fan},{now}'
    print(fanONtemp, fanOFFtemp)
    flogger(f'now={now}')

    f = open(datafile,mode='w',encoding='utf-8')
    f.write(data)
    f.close

    # send values to influxdb
    ts = str(datetime.datetime.now()).split('.')[0].replace(' ', 'T')
    json_data = [{"measurement": "dome_temp_inside","time": f"{ts}","fields": {"value": temp}}]
    write_api.write(INFLUX_BUCKET, INFLUX_ORG, json_data, time_precision='s')

    json_data = [{"measurement": "dome_humi_inside","time": f"{ts}","fields": {"value": humi}}]
    write_api.write(INFLUX_BUCKET, INFLUX_ORG, json_data, time_precision='s')

    json_data = [{"measurement": "dome_fan","time": f"{ts}","fields": {"value": iFan}}]
    write_api.write(INFLUX_BUCKET, INFLUX_ORG, json_data, time_precision='s')


while True:
    loop()
    time.sleep(60)