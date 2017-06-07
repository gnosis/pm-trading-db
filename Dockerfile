FROM ubuntu:14.04
RUN apt-get update && apt-get install -y -q curl python-dev \
    libreadline-dev libbz2-dev libssl-dev libsqlite3-dev git wget \
    libxml2-dev libxslt1-dev python-pip build-essential automake libtool \
    libffi-dev libgmp-dev pkg-config libpq-dev postgresql-client

COPY . /gnosisdb/
WORKDIR /gnosisdb

RUN pip install -qr /gnosisdb/requirements.txt
RUN git clone https://github.com/ethereum/pyethereum/ && cd pyethereum && python setup.py install
