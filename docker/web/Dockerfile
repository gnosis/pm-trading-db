FROM ubuntu:14.04

RUN apt-get update && apt-get install -y -q curl python-dev software-properties-common \
    libreadline-dev libbz2-dev libssl-dev git wget \
    python-pip build-essential python-software-properties automake libtool pkg-config
RUN add-apt-repository "deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main" && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
RUN apt-get update && apt-get install -y postgresql-9.6 postgresql-client-10

RUN pip install --upgrade pip
RUN pip install pyOpenSSL cryptography idna certifi

ADD requirements.txt /tmp/requirements.txt
RUN pip install -qr /tmp/requirements.txt

RUN mkdir -p /root/var/run/celery

COPY . /gnosisdb/
WORKDIR /gnosisdb
ENTRYPOINT ["/bin/bash", "/gnosisdb/scripts/entrypoint.sh"]
