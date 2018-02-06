FROM python:3-stretch

# Remove this when secp256k1 get supported in debian stretch
RUN apt-get update && apt-get install -y libsecp256k1-dev

# Signal handling for PID1
RUN wget https://github.com/Yelp/dumb-init/releases/download/v1.2.1/dumb-init_1.2.1_amd64.deb && \
    dpkg -i dumb-init_*.deb && \
    rm -f dumb-init_*.deb

RUN mkdir -p /root/var/run/celery

WORKDIR /gnosisdb
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
