FROM python:3-stretch

# Signal handling for PID1 https://github.com/krallin/tini
ENV TINI_VERSION v0.17.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main" > /etc/apt/sources.list.d/pgdg.list  && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
# Remove secp256k1 when it gets supported in debian stretch
RUN apt-get update && apt-get install -y postgresql-client-10 libsecp256k1-dev

RUN mkdir -p /root/var/run/celery

WORKDIR /gnosisdb
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["/tini", "--"]
