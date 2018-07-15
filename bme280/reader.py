#!/usr/bin/python3
import os
import threading
import sys
from Adafruit_BME280 import *
from datetime import datetime
from elasticsearch import Elasticsearch

def readSensor():
  # Timestamp for report
  timestamp = datetime.utcnow()

  # Recursively initiate next reading in a minute
  threading.Timer(60-float(datetime.utcnow().strftime('0.%f')), readSensor).start()

  degrees = sensor.read_temperature() + t_compensation
  pascals = sensor.read_pressure()
  pressure = pascals / 100 * 0.75006375541921
  humidity = sensor.read_humidity()

  report = { 'timestamp': timestamp, 'sensor': 'bme280', 'temperature': degrees, 'humidity': humidity, 'pressure': pressure }
  if es_host:
    send2es(report)
  else:
    print("Time UTC: {}\tt={:0.2f} h={:0.2f} p={:0.2f}".format(timestamp, degrees, humidity, pressure))

def send2es(data):
  """ Initiate connection to Elasticsearch and send data as a single document.
  data - dictionary/JSON to be sent
  """

  i = 'metrics_{}'.format(datetime.now().strftime('%m.%y'))
  es.index(index=i, doc_type='measurement', body=data)

if __name__ == "__main__":

  print("Script started")

  try:
    es_host = os.environ['ELASTICSEARCH_URL']
    es_user = os.environ['ELASTICSEARCH_USER']
    es_pass = os.environ['ELASTICSEARCH_PASSWORD']
    es = Elasticsearch(es_host, http_auth=(es_user, es_pass))
  except KeyError:
    es_host = None
  try:
    t_compensation = float(os.environ['T_COMPENSATION'])
  except KeyError:
    t_compensation = 0

  sensor = BME280(t_mode=BME280_OSAMPLE_2, 
                  p_mode=BME280_OSAMPLE_8, 
                  h_mode=BME280_OSAMPLE_1, 
                  filter=BME280_FILTER_16, 
                  address=0x76)

  threading.Timer(60-float(datetime.utcnow().strftime('%S.%f')), readSensor).start()
  print("Waiting for next minute to start loop...")
