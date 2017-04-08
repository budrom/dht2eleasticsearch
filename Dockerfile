FROM resin/rpi-raspbian:jessie

RUN apt-get update && apt-get remove python && apt-get autoremove && apt-get install -y \
    git-core \
    build-essential \
    gcc \
    python3 \
    python3-dev \
    python3-pip \
    python3-virtualenv \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    pip3 install pyserial && \
    cd /tmp/ && git clone git://git.drogon.net/wiringPi && \
    cd wiringPi && ./build && \
    pip3 install wiringpi2 elasticsearch && \
    cd /tmp/ && git clone https://github.com/adafruit/Adafruit_Python_DHT.git && \
    cd Adafruit_Python_DHT && python setup.py install && \
    cd / && apt-get remove git-core build-essential python3-dev && \
    apt-get -y autoremove && apt-get clean && rm -rf /tmp/*

COPY dhtReader.py /
ENTRYPOINT ["python", "dhtReader.py"]
