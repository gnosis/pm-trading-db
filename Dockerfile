FROM ubuntu:14.04
RUN apt-get update && apt-get install -y -q curl python-dev \
    libreadline-dev libbz2-dev libssl-dev libsqlite3-dev git wget \
    libxml2-dev libxslt1-dev python-pip build-essential automake libtool \
    libffi-dev libgmp-dev pkg-config libpq-dev postgresql-client
COPY . /gnosisdb/
RUN wget https://pypi.python.org/packages/9d/ba/80910bbed2b4e646a6adab4474d2e506744c260c7002a0e6b41ef8750d8d/pkgconfig-1.2.2.tar.gz#md5=81a8f6ef3371831d081e03db39e09683 && tar -xvf pkgconfig-1.2.2.tar.gz && cd pkgconfig-1.2.2 && python setup.py install
RUN pip install -qr /gnosisdb/requirements.txt
RUN git clone https://github.com/ethereum/pyethereum/ && cd pyethereum && python setup.py install
RUN pip install --user /gnosisdb/lib/django-ether-logs-0.1.tar.gz

### MongoDB ###
# Add the package verification key
# RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10

# Add MongoDB to the repository sources list
# RUN echo "deb http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list

# Update the repository sources list once more
# RUN apt-get update

# Install MongoDB package (.deb)
# RUN apt-get install -y mongodb-org

# Create the default data directory
# RUN mkdir -p /data/db /data/configdb \
# 	&& chown -R mongodb:mongodb /data/db /data/configdb

### End MongoDB ###

WORKDIR /gnosisdb
