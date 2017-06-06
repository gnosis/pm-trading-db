FROM ubuntu:14.04
RUN apt-get update && apt-get install -y -q curl python-dev \
    libreadline-dev libbz2-dev libssl-dev libsqlite3-dev git wget \
    libxml2-dev libxslt1-dev python-pip build-essential automake libtool \
    libffi-dev libgmp-dev pkg-config libpq-dev postgresql-client
COPY . /gnosisdb/
RUN wget https://pypi.python.org/packages/9d/ba/80910bbed2b4e646a6adab4474d2e506744c260c7002a0e6b41ef8750d8d/pkgconfig-1.2.2.tar.gz#md5=81a8f6ef3371831d081e03db39e09683 && tar -xvf pkgconfig-1.2.2.tar.gz && cd pkgconfig-1.2.2 && python setup.py install
RUN pip install -qr /gnosisdb/requirements.txt
RUN git clone https://github.com/ethereum/pyethereum/ && cd pyethereum && python setup.py install

WORKDIR /gnosisdb
