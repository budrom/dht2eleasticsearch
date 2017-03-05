#!/usr/bin/python

import os
import threading
import time
from datetime import datetime
import Adafruit_DHT
from elasticsearch import Elasticsearch


sensor = Adafruit_DHT.DHT22
try:
  pin = int(os.environ['GPIO_PIN'])
except KeyError:
  print('GPIO pin not specified! Aborting.')
  exit(1)
try:
  es_host = os.environ['ES_HOST']
except KeyError:
  es_host = None
try: 
  es_port = int(os.environ['ES_PORT'])
except KeyError:
  es_port = 9200


def send2es(data):

  es = Elasticsearch([ { 'host': es_host, 'port': es_port } ])

  
  i = 'metrics_{}'.format(datetime.now().strftime('%m.%y'))
  es.index(index=i, doc_type='dht', body=data)


def readSensor():

  timestamp = datetime.utcnow()
  threading.Timer(60-float(datetime.utcnow().strftime('0.%f')), readSensor).start()

  # read_retry method will retry up to 15 times to get a sensor reading (waiting 2 seconds between each retry).
  humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
  # temperature correction on empirically discovered delta
  temperature -= 0.6

  if humidity is not None and temperature is not None:
      print('{0} : Temperature={1:0.1f}*C  Humidity={2:0.1f}%'.format(timestamp.strftime('%H:%M:%S.%f'),temperature, humidity))
      if es_host is not None:
        data = {"timestamp": timestamp, "temperature": temperature, "humidity": humidity/100}
        send2es(data)
  else:
      print('Failed to get reading.')


if __name__ == "__main__":
  print("Script started.")
  threading.Timer(60-float(datetime.utcnow().strftime('%S.%f')), readSensor).start()
  print("Waiting for next minute to start loop...")

