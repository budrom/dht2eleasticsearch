#!/usr/bin/python

import os
import threading
import time
from datetime import datetime
import Adafruit_DHT
from elasticsearch import Elasticsearch
from statistics import mean


def send2es(data):
  """ Initiate connection to Elasticsearch and send data as a single document.
  data - dictionary/JSON to be sent
  """

  es = Elasticsearch([ { 'host': es_host, 'port': es_port } ])

  
  i = 'metrics_{}'.format(datetime.now().strftime('%m.%y'))
  es.index(index=i, doc_type='dht', body=data)


def readSensor(pin):
  """ Read single sensor values.
  Temperature correction is added based on comparing with usual termomether
  """

  # read_retry method will retry up to 15 times to get a sensor reading (waiting 2 seconds between each retry).
  humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
  # temperature correction on empirically discovered delta
  temperature -= 0.6

  if humidity is not None and temperature is not None:
      return temperature, humidity
      print('{0} : Temperature={1:0.1f}*C  Humidity={2:0.1f}%'.format(timestamp.strftime('%H:%M:%S.%f'),temperature, humidity))
      if es_host is not None:
        data = {"timestamp": timestamp, "temperature": temperature, "humidity": humidity/100}
        send2es(data)
  else:
      print('Failed to get reading.')

def readSensorArray(sensors):
  """ Read multiple sensors and compile data from all of them into one report. 
  sensors - array of GPIO pin numbers to connect to sensors.
  """

  # Timestamp for report
  timestamp = datetime.utcnow()

  # Recursively initiate next reading in a minute
  threading.Timer(60-float(datetime.utcnow().strftime('0.%f')), readSensorArray, [sensors]).start()

  T = []
  H = []

  for sensor in sensors:
    temperature, humidity = readSensor(pin=sensor)
    T.append(temperature)
    H.append(humidity/100)
  
  temperature = mean(T)
  humidity = mean(H)
  deltaT = max(T)-min(T)
  deltaH = max(H)-min(H)

  report = { "timestamp": timestamp, "temperature": temperature, "humidity": humidity, "delta_t": deltaT, "delta_h": deltaH, "sensors_quantity": len(sensors) }
  print("Time UTC: {} t={:0.2f} h={:0.2f} d_t={:0.2f} d_h={:0.2f} sensors: {}".format(timestamp, temperature, humidity, deltaT, deltaH, len(sensors))) 
  if es_host:
    send2es(report)


if __name__ == "__main__":

  print("Script started")

  sensor_types = { '11': Adafruit_DHT.DHT11,
                   '22': Adafruit_DHT.DHT22,
                   '2302': Adafruit_DHT.AM2302 }

  try:
    sensor_type = os.environ["SENSOR_TYPE"]
    if sensor_type not in ['11','22','2302']:
      print('Sensor type must be one either 11, 22 or 2302! Aborting.')
      exit(1)
    print("Sensor type: {}".format(sensor_type))
  except KeyError:
    print('Sensor type not specified, assuming DHT22...')
    sensor_type = "22"
  try:
    pins = os.environ['GPIO_PINS'].split(',')
    print('GPIO pins: {}'.format(pins))
  except KeyError:
    print('GPIO pin(s) must be specified! Aborting.')
    exit(1)
  try:
    es_host = os.environ['ES_HOST']
  except KeyError:
    es_host = None
  try:
    es_port = int(os.environ['ES_PORT'])
  except KeyError:
    es_port = 9200

  sensor = sensor_types[sensor_type]

  threading.Timer(60-float(datetime.utcnow().strftime('%S.%f')), readSensorArray, [pins]).start()
  print("Waiting for next minute to start loop...")

