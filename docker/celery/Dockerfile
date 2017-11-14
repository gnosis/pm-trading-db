FROM ubuntu:14.04
RUN apt-get update && apt-get install -y -q curl python-dev \
    libreadline-dev libbz2-dev libssl-dev libxslt1-dev git wget \
    libxml2-dev python-pip build-essential automake libtool \
    libffi-dev libgmp-dev pkg-config libpq-dev postgresql-client

RUN pip install --upgrade pip
RUN pip install pyOpenSSL cryptography idna certifi

ADD requirements.txt /tmp/requirements.txt
RUN pip install -qr /tmp/requirements.txt
RUN mkdir -p /root/var/run/celery
COPY . /gnosisdb/
WORKDIR /gnosisdb
ENV C_FORCE_ROOT 1
ENTRYPOINT [ "/bin/sh" ]
