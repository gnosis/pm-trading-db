# gnosisdb
Gnosis Core Database Layer

## Setup

### Install Docker and Docker Compose
* First, install docker: https://docs.docker.com/engine/installation/.
* Then, install docker compose: https://docs.docker.com/compose/install/
* Change your working directory: `cd gnosisdb`

### Build containers
The application is made up of several container images that are linked together using docker-compose. Before running the application, build the images:
`sudo docker-compose build`

### Run application
Start the gnosisdb server simply by bringing up the set of containers:
`sudo docker-compose up`
