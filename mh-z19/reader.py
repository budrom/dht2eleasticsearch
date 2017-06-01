#!/usr/bin/python3
import os
import threading
import serial
import sys
from datetime import datetime
from elasticsearch import Elasticsearch
import time

MHZ19_SIZE = 9
MZH19_READ = [0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79]

def read_mh_z19():
    """ Read the CO2 PPM concenration from a MH-Z19 sensor"""

    result = read_mh_z19_with_temperature()
    if result is None:
        return None
    ppm, temp, s = result
    return ppm, temp, s


def read_mh_z19_with_temperature():
    """ Read the CO2 PPM concenration and temperature from a MH-Z19 sensor"""

    sbuf = bytearray()
    starttime = time.time()
    finished = False
    timeout = 2
    res = None
    sensor.write(MZH19_READ)
    while not finished:
        mytime = time.time()
        if mytime - starttime > timeout:
            return None

        if sensor.inWaiting() > 0:
            sbuf += sensor.read(1)

            if len(sbuf) == MHZ19_SIZE:
                res = (sbuf[2]*256 + sbuf[3], sbuf[4] - 40, 1 - sbuf[5]/64)
                finished = True

        else:
            time.sleep(.1)

    return res

def readSensor():
  # Timestamp for report
  timestamp = datetime.utcnow()

  # Recursively initiate next reading in a minute
  threading.Timer(30-float(datetime.utcnow().strftime('0.%f')), readSensor).start()

  ppm, T, S = read_mh_z19()

  report = { "timestamp": timestamp, "co2": ppm, "uncertainty": S }
  if es_host:
    send2es(report)
  print("Time UTC: {}\tco2={}\tuncertainty={}".format(timestamp, ppm, S))

def send2es(data):
  """ Initiate connection to Elasticsearch and send data as a single document.
  data - dictionary/JSON to be sent
  """

  i = 'metrics_{}'.format(datetime.now().strftime('%m.%y'))
  es.index(index=i, doc_type='mh-z19', body=data)

if __name__ == "__main__":

  print("Script started")

  try:
    es_host = os.environ['ES_HOST']
  except KeyError:
    es_host = None
  try:
    es_port = int(os.environ['ES_PORT'])
  except KeyError:
    es_port = 9200

  sensor = serial.Serial('/dev/ttyAMA0',
                          baudrate=9600,
                          bytesize=serial.EIGHTBITS,
                          parity=serial.PARITY_NONE,
                          stopbits=serial.STOPBITS_ONE,
                          timeout=1.0)

  if es_host:
    es = Elasticsearch([ { 'host': es_host, 'port': es_port } ])
  threading.Timer(60-float(datetime.utcnow().strftime('%S.%f')), readSensor).start()
  print("Waiting for next minute to start loop...")
