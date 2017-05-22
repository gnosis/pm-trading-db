FROM ubuntu:14.04
RUN apt-get update && apt-get install -y -q python-all python-pip
COPY . /gnosisdb/
RUN pip install -qr /gnosisdb/requirements.txt

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
# EXPOSE 8080
# EXPOSE 27017

# CMD mongod&
