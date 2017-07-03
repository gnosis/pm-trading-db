# gnosisdb
Gnosis Core Database Layer

## Setup

### Install Docker and Docker Compose
* First, install docker: https://docs.docker.com/engine/installation/.
* Then, install docker compose: https://docs.docker.com/compose/install/
* Change your working directory: `cd gnosisdb`

### Build containers
The application is made up of several container images that are linked together using docker-compose. Before running the application, build the images:
`docker-compose build --force-rm`

## Create a Django superuser
Run the Web container with the following command and create a super user in order to access the /admin interface.
`docker-compose run web bash`

`python manage.py createsuperuser`

### Run application
Start the gnosisdb server simply by bringing up the set of containers:
`sudo docker-compose up`

## Development
For development purposes you may want to run a testrpc node on your machine. To do so, run:

`testrpc --gasLimit 400000000 -d`

The -d option allows you to get the same address everytime a contract is deployed. You will not have to update your django settings everytime a new testrpc server is running.

Install the Gnosis-contracts repo (https://github.com/giacomolicari/gnosis-contracts) following the provided instrunctions.
Change your working dir to /contracts and deploy the contracts onto the running testrpc with the command:

`python ethdeploy.py --f deploy/basicFramework.json --gas 40000000`

The execution will furnish all the contracts' addesses. Now open /settings/local.py file and modify the addresses in ETH_EVENTS for the following instances:
* Centralized Oracle Factory
* Event Factory
* Standard Market Factory
* Ultimate Oracle Factory

Make sure that ETHEREUM_NODE_HOST variable in settings.local points to your wlan ip address serving testrpc.

Run `docker-compose build` to apply the code changes and then `docker-compose up` to get GNOSISDB up and running.
Open your browser and go to http://localhost:8000/admin, provide your superuser username and password.
You should now see something like this:

![alt_text](https://github.com/gnosis/gnosisdb/blob/master/img/django_admin_overview.png)

Create now a Celery periodic task.

![alt text](https://github.com/gnosis/gnosisdb/blob/master/img/django_celery.png)

A test script was created on gnosis-contracts/scripts. This emulates the creation of oracles, events and markets.
Run it with:

`python create_oracles.py --testrpc_host 0.0.0.0 --testrpc_port 8545 --ipfs_host http://192.168.1.165 --ipfs_port 5001 --gas 10000000`

Change the --ipfs_host option with your wlan ip address. The script will communicate to the IPFS Docker Container.
