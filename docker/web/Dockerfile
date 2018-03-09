FROM python:3-slim-stretch

RUN mkdir -p /root/var/run/celery
WORKDIR /gnosisdb

# Signal handling for PID1 https://github.com/krallin/tini
ENV TINI_VERSION v0.17.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

ENV BUILD_DEP build-essential pkg-config libssl-dev libsecp256k1-dev
ENV POSTGRES_DEP wget gnupg

RUN apt-get update && \
    apt-get install -yq --no-install-recommends $POSTGRES_DEP

RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main" > /etc/apt/sources.list.d/pgdg.list && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
# Remove secp256k1 when it gets supported in debian stretch
COPY requirements.txt ./
RUN apt-get update && \
    apt-get install -yq --no-install-recommends postgresql-client-10 $BUILD_DEP && \
    pip install --no-cache-dir -r requirements.txt && \
    find /usr/local \
        \( -type d -a -name test -o -name tests \) \
        -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
        -exec rm -rf '{}' + && \
    apt-get remove --purge -y $BUILD_DEP $POSTGRES_DEP && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .

ENTRYPOINT ["/tini", "--"]

# RUN useradd --user-group --shell /bin/false python
# USER python
