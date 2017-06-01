FROM resin/rpi-raspbian:jessie

RUN apt-get update && apt-get remove python && apt-get autoremove && apt-get install -y \
    python3 \
    python3-urllib3 \
    python3-dev \
    python3-pip \
    python3-virtualenv \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    pip3 install pyserial elasticsearch && \
    apt-get remove python3-dev python3-pip && \
    apt-get -y autoremove && apt-get clean && rm -rf /tmp/*

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-smbus \
    python3-dev \
    build-essential git \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* && \
    cd /tmp/ && git clone https://github.com/adafruit/Adafruit_Python_GPIO.git && \
    cd Adafruit_Python_GPIO && python setup.py install && \
    cd / && git clone https://github.com/dewhisna/Adafruit_Python_BME280.git && \
    apt-get remove python3-dev python3-pip build-essential git && \
    apt-get -y autoremove && apt-get clean && rm -rf /tmp/*

COPY reader.py /Adafruit_Python_BME280/
ENTRYPOINT ["python", "/Adafruit_Python_BME280/reader.py"]
