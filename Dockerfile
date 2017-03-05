FROM resin/rpi-raspbian:jessie

RUN apt-get update && apt-get install -y \
    git-core \
    build-essential \
    gcc \
    python \
    python-dev \
    python-pip \
    python-virtualenv \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* && \
    pip install pyserial && \
    cd /tmp/ && git clone git://git.drogon.net/wiringPi && \
    cd wiringPi && ./build && \
    pip install wiringpi2 elasticsearch && \
    cd /tmp/ && git clone https://github.com/adafruit/Adafruit_Python_DHT.git && \
    cd Adafruit_Python_DHT && python setup.py install && \
    cd / && apt-get remove git-core build-essential python-dev && \
    apt-get -y autoremove && apt-get clean && rm -rf /tmp/*

COPY dht2elasticsearch.py /
ENTRYPOINT ["python", "dht2elasticsearch.py"]
