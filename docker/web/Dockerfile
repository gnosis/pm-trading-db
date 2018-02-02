FROM fpco/pid1:16.04

RUN apt-get update && apt-get install -y -q curl python-dev software-properties-common \
    libreadline-dev libbz2-dev libssl-dev git wget libffi-dev \
    python-pip build-essential python-software-properties automake libtool pkg-config

RUN add-apt-repository "deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main" && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN apt-get update && apt-get install -y postgresql-9.6 postgresql-client-10

RUN pip install --upgrade pip
RUN pip install --upgrade pyOpenSSL cryptography idna certifi ndg-httpsclient pyasn1

ADD requirements.txt /tmp/requirements.txt
RUN pip install -qr /tmp/requirements.txt

RUN mkdir -p /root/var/run/celery

COPY . /gnosisdb/
WORKDIR /gnosisdb
ENTRYPOINT ["/sbin/pid1"]
