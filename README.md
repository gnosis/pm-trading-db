[![Build Status](https://travis-ci.org/gnosis/gnosisdb.svg?branch=master)](https://travis-ci.org/gnosis/gnosisdb)
[![Coverage Status](https://coveralls.io/repos/github/gnosis/gnosisdb/badge.svg?branch=master)](https://coveralls.io/github/gnosis/gnosisdb?branch=master)
![Python 3.6](https://img.shields.io/badge/Python-3.6-blue.svg)
![Django 2](https://img.shields.io/badge/Django-2-blue.svg)

# GnosisDB
Gnosis Core Database Layer

## Index of contents

- [Installation](#installation)
- [Django settings](#django-settings)
- [How to implement your own AddressGetter and EventReceiver](#how-to-implement-your-own-addressgetter-and-eventreceiver)
- [REST API](#rest-api)
- [Resync Database](#resync-database)
- [Backup Database](#backup-database)
- [Tournament Setup](#tournament-setup)
- [GnosisDB deployment with Kubernetes](#gnosisdb-deployment-in-kubernetes)
- [Contributors](#contributors)

Installation
------------

### Install Docker and Docker Compose
* First, install docker: https://docs.docker.com/engine/installation/.
* Then, install docker compose: https://docs.docker.com/compose/install/
* Clone the repository and change your working directory:

```
git clone https://github.com/gnosis/gnosisdb.git
cd gnosisdb
```

### Build containers
The application is made up of several container images that are linked together using docker-compose. Before running the application, build the images:

`docker-compose build --force-rm`

### Create a Django superuser
Enter the Web container's command line with the following command:

```
docker-compose run web sh
```

Once inside, create a super user in order to access the /admin interface.

```
python manage.py migrate
python manage.py createsuperuser
```

You may exit the web container shell with:

```
exit
```

### Run application
Start the gnosisdb server simply by bringing up the set of containers:

`sudo docker-compose up`

You can access it on http://localhost:8000 and the admin is on http://localhost:8000/admin

You will need to have the following ports open on your machine for this to work:

- 5432: PostgreSQL
- 4001: IPFS peering port
- 5001: IPFS API server
- 5672: RabbitMQ
- 8000: NGINX serving a Django administrative app

### Populate database
To populate database and retrieve some information, the easiest is to use [gnosis.js](https://github.com/gnosis/gnosis.js)
with a local blockchain (Ganache-cli).

[Gnosis.js](https://github.com/gnosis/gnosis.js) will deploy gnosis smart contracts and run some operations between them (emulates the creation of oracles, events and markets),
so you will have information in your private blockchain for gnosisdb to index.

```
git clone https://github.com/gnosis/gnosis.js.git
cd gnosis.js
npm install
```

You will need to have Ganache-cli running, which has been downloaded by previous `npm install`. So in the same gnosis.js folder:

`./node_modules/.bin/ganache-cli --gasLimit 40000000 -d -h 0.0.0.0 -i 437894314312`

The -d option allows you to get the same address everytime a contract is deployed. You will not have to update your django settings everytime a new Ganache server is running.

The -h option tells Ganache to listen on all interfaces, including the bridge interfaces which are exposed inside of the docker containers.
This will allow a setting of `ETHEREUM_NODE_HOST = '172.x.x.x'` to work for the Celery worker.

The -i option sets the network id.

Open another window and go to the gnosis.js folder, deploy the contracts and run gnosisdb tests. This emulates the creation of oracles, events and markets.
Docker containers must be up because *tests require ipfs, and* of course *Ganache-cli* too:

```
npm run migrate
npm run test-gnosisdb
```

The execution will furnish all the contracts' addesses in the `node_modules/@gnosis.pm/gnosis-core-contracts/build/contracts` folder as parts of the build artifacts.
You should also see the addresses displayed in your console.

You can verify that the addresses in ETH_EVENTS specified in `config/settings/local.py` match what is displayed by the console for all the contracts including:

* Centralized Oracle Factory
* Event Factory
* Standard Market Factory

Open your browser and go to http://localhost:8000/admin, provide your superuser username and password.
You should now see something like this:

![Admin overview](https://github.com/gnosis/gnosisdb/blob/master/img/django_admin_overview.png)

Create now a Celery periodic task. This _Event Listener_ task will start indexing and processing information in the blockchain.

![Periodic task management](https://github.com/gnosis/gnosisdb/blob/master/img/django_celery.png)


### Development
Every time you do a change in the source code run `docker-compose build` to apply the code changes and
then `docker-compose up` to get GNOSISDB up and running.


Django Settings
---------------

GnosisDB comes with a production settings file that you can edit.

##### ALLOWED_HOSTS
Specify the list of allowed hosts to connect to GnosisDB:

`ALLOWED_HOSTS = ['.gnosis.pm', '127.0.0.1', 'localhost']`

##### ADMINS
Specify your application administrators:

```
ADMINS = (
    ('Batman', 'batman@gnosis.pm'),
    ('Robin', 'robin@gnosis.pm'),
)
```

##### ETHEREUM
Provide an Ethereum _host_, _port_ and _SSL (0, 1)_. Use _SSL = 1_ only if your Ethereum host supports HTTPS/SSL.
Communication with node will use **RPC through HTTP/S**

```
ETHEREUM_NODE_HOST = os.environ['ETHEREUM_NODE_HOST']
ETHEREUM_NODE_PORT = os.environ['ETHEREUM_NODE_PORT']
ETHEREUM_NODE_SSL = bool(int(os.environ['ETHEREUM_NODE_SSL']))
```

You can also provide an **IPC path** to a node running locally, which will be faster.
You can use the environment variable  _ETHEREUM_IPC_PATH_.
If set, it will override _ETHEREUM_NODE_HOST_ and _ETHEREUM_NODE_PORT_, so **IPC will
be used instead of RPC**:

```
ETHEREUM_IPC_PATH = os.environ['ETHEREUM_IPC_PATH']
```

Number of concurrent threads connected to the ethereum node can be configured:

```
ETHEREUM_MAX_WORKERS = os.environ['ETHEREUM_MAX_WORKERS']
```

##### IPFS
Provide an IPFS host and port:

```
IPFS_HOST = os.environ['IPFS_HOST']
IPFS_PORT = os.environ['IPFS_PORT']
```

##### RABBIT MQ
RabbitMQ is the default Celery's messaging broker, other brokers are Redis and Amazon SQS.<br/>
More info about Celery's brokers at [this link](http://docs.celeryproject.org/en/latest/getting-started/brokers/index.html).<br/>

```
RABBIT_HOSTNAME = os.environ['RABBIT_HOSTNAME']
RABBIT_USER = os.environ['RABBIT_USER']
RABBIT_PASSWORD = os.environ['RABBIT_PASSWORD']
RABBIT_PORT = os.environ['RABBIT_PORT']
RABBIT_QUEUE = os.environ['RABBIT_QUEUE']
BROKER_URL = 'amqp://{user}:{password}@{hostname}:{port}/{queue}'.format(
    user=RABBIT_USER,
    password=RABBIT_PASSWORD,
    hostname=RABBIT_HOSTNAME,
    port=RABBIT_PORT,
    queue=RABBIT_QUEUE
)
```
##### LMSR MARKET MAKER
You need to specify the LMSR Market Maker address you have deployed previously (to discover how to do that please take a look at [gnosis-contracts](https://github.com/gnosis/gnosis-contracts):

`LMSR_MARKET_MAKER = '2f2be9db638cb31d4143cbc1525b0e104f7ed597'`

##### GNOSIS ETHEREUM CONTRACTS
The ETH_EVENTS array variable allows you to define and map a list of addressess to their related event listeners.<br/>
Create a new array variable in your settings file and call it ETH_EVENTS as follows:

```
ETH_EVENTS = [
    {
        'ADDRESSES': ['254dffcd3277c0b1660f6d42efbb754edababc2b'],
        'EVENT_ABI': '... ABI ...',
        'EVENT_DATA_RECEIVER': 'yourmodule.event_receivers.YourReceiverClass',
        'NAME': 'Your Contract Name',
        'PUBLISH': True,
    },
    {
        'ADDRESSES_GETTER': 'yourmodule.address_getters.YouCustomAddressGetter',
        'EVENT_ABI': '... ABI ...',
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.MarketInstanceReceiver',
        'NAME': 'Standard Markets Buy/Sell/Short Receiver'
    }
]
```
Please read out the "How to implement your own AddressGetter and EventReceiver" paragraph for a deeper explication on how to develop your listeners.

How to implement your own AddressGetter and EventReceiver
---------------------------------------------------------
Let's consider the ETH_EVENTS settings varable:
```
ETH_EVENTS = [
    {
        'ADDRESSES': ['254dffcd3277c0b1660f6d42efbb754edababc2b'],
        'EVENT_ABI': '... ABI ...',
        'EVENT_DATA_RECEIVER': 'yourmodule.event_receivers.YourReceiverClass',
        'NAME': 'Your Contract Name',
        'PUBLISH': True,
    },
    {
        'ADDRESSES_GETTER': 'yourmodule.address_getters.YouCustomAddressGetter',
        'EVENT_ABI': '... ABI ...',
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.MarketInstanceReceiver',
        'NAME': 'Standard Markets Buy/Sell/Short Receiver'
    }
]
```
As you can see, the properties that come into play are:
* ADDRESSES, the list of contract's addresses you may want to watch and listen to. Four formats are accepted:
  - 0x checksumed address, like _0x254dffcd3277C0b1660F6d42EFbB754edaBAbC2B_
  - 0x plain address, like _0x254dffcd3277c0b1660f6d42efbb754edababc2b_
  - Non 0x checksumed address _254dffcd3277C0b1660F6d42EFbB754edaBAbC2B_
  - Non 0x plain address, like _254dffcd3277c0b1660f6d42efbb754edababc2b_
* ADDRESSES_GETTER, a custom addresses getter class
* EVENT_ABI, the contract's JSON ABI in string format
* EVENT_DATA_RECEIVER, a custom event data receiver class
* NAME, the contract name
* PUBLISH, it denotes that this part of the config should have the addresses field in it published on that REST endpoint (see REST API paragraph)

*ADDRESSES_GETTER* and *EVENT_DATA_RECEIVER* will be resolved when the application starts, throwing an exception if not found.
*ADDRESSES* will be check too, and an exception will be thrown if non valid address is found. Duplicated addresses will be removed too.

##### EVENT DATA RECEIVER
An Event Data Receiver is responsible for storing data into a database.<br/>
All the receivers must inherit from [**django_eth_events.chainevents.AbstractEventReceiver**](https://github.com/gnosis/django-eth-events/blob/master/django_eth_events/chainevents.py#L16) class and implement the **save(self, decoded_event, block_info)** method.

Below the CentralizedOracleFactoryReceiver. It instantiates the CentralizedOracleSerializer, then verify if input data is valid, and finally save everything into the database.

```
from django_eth_events.chainevents import AbstractEventReceiver


class CentralizedOracleFactoryReceiver(AbstractEventReceiver):

    def save(self, decoded_event, block_info):
        serializer = CentralizedOracleSerializer(data=decoded_event, block=block_info)
        if serializer.is_valid():
            serializer.save()
            logger.info('Centralized Oracle Factory Result Added: {}'.format(dumps(decoded_event)))
        else:
            logger.warning(serializer.errors)
```

##### ADDRESSES GETTER
In case you wouldn't directly declare the contract address/addresses, you should specify an Addresses Getter class instead.<br/>
An Addresses Getter class must inherit from [**django_eth_events.chainevents.AbstractAddressesGetter**](https://github.com/gnosis/django-eth-events/blob/master/django_eth_events/chainevents.py#L5) and implement two methods:
* __get_addresses__(self), returns a list of strings (addresses)
* __contains__(self, address), returns True if the given address is in the addresses list, False otherwise

Take a look at ContractAddressGetter:

```
from gnosisdb.relationaldb.models import Contract
from django.core.exceptions import ObjectDoesNotExist
from django_eth_events.chainevents import AbstractAddressesGetter


class ContractAddressGetter(AbstractAddressesGetter):
    """
    Returns the addresses used by event listener in order to filter logs triggered by Contract Instances
    """
    class Meta:
        model = Contract

    def get_addresses(self):
        """
        Returns list of ethereum addresses
        :return: [address]
        """
        return list(self.Meta.model.objects.values_list('address', flat=True))

    def __contains__(self, address):
        """
        Checks if address is contained on the Contract collection
        :param address: ethereum address string
        :return: Boolean
        """
        try:
            self.Meta.model.objects.get(address=address)
            return True
        except ObjectDoesNotExist:
            return False
```

REST API
-------
GnosisDB comes with a handy RESTful API. Run GnosisDB, open your Web browser and connect to http://localhost:8000. You will get all the relevant API endpoints and their input/return data.

RESYNC DATABASE
----------------
To resync database with the blockchain, first we must delete every information that is on the database with the following task:

`python manage.py cleandatabase`

Then we must force the daemon to resync everything again:

`python manage.py resync_daemon`


BACKUP DATABASE
----------------
If you use `python manage.py db_dump` you will get a backup of the database on the mail (it will be generated in _/tmp_ folder of the machine),
using custom Postgres format (as recommended on the docs). If you want to convert it to standard SQL:

`pg_restore -f mydatabase.sqlc mydatabase.dump`

TOURNAMENT SETUP
----------------
To configure a custom tournament, you need to first need to [deploy the smart contracts needed on the chosen public test network](https://gnosis-apollo.readthedocs.io/en/latest/smart-contracts.html). For this setup guide, we will assume the choice of [Rinkeby](https://www.rinkeby.io/#stats).

Take note of your deployed addresses for [AddressRegistry](https://github.com/gnosis/olympia-token#addressregistry) and the [PlayToken](https://github.com/gnosis/olympia-token#playtoken). You can find them with `npm run truffle networks`. This guide will assume the following as the deployed addresses, though you will have something different:

```
OlympiaToken: 0x2924e2338356c912634a513150e6ff5be890f7a0
AddressRegistry: 0x12f73864dc1f603b2e62a36b210c294fd286f9fc
```

Clone the `gnosisdb` repository:

```sh
git clone https://github.com/gnosis/gnosisdb.git
cd gnosisdb
```

Change these lines with your custom values in **config/settings/rinkeby.py**:

```
TOURNAMENT_TOKEN = '0x2924e2338356c912634a513150e6ff5be890f7a0'

...

os.environ['GENERIC_IDENTITY_MANAGER_ADDRESS'] = '0x12f73864dc1f603b2e62a36b210c294fd286f9fc'
```

Add your ethereum account too for token issuance:

```
ETHEREUM_DEFAULT_ACCOUNT = '0x847968C6407F32eb261dC19c3C558C445931C9fF'
ETHEREUM_DEFAULT_ACCOUNT_PRIVATE_KEY = 'a3b12a165350ab3c7d1ecd3596096969db2839c7899a3b0b39dd479fdd5148c7'
```

If you don't have the private key for your account, but you do know the BIP39 mnemonic for it, you may enter your mnemonic into [Ganache](http://truffleframework.com/ganache/) to recover the private key.

You may have a running Geth node connected to [Rinkeby](https://www.rinkeby.io/#geth) on the same machine:

```sh
geth --rinkeby --rpc
```

Configure an HTTP provider on **config/settings/rinkeby.py**:

```
ETHEREUM_NODE_HOST = '172.17.0.1'
ETHEREUM_NODE_PORT = 8545
ETHEREUM_NODE_SSL = 0
```

In order to use this node through IPC instead of an HTTP RPC provider, you will want to take note of the IPC endpoint for your Geth instance. If you've just started Geth, look for a line in the console output indicating this information:

```
INFO [01-01|00:00:00] IPC endpoint opened                      url=/home/user/.ethereum/rinkeby/geth.ipc
```

Make sure the socket file is visible from the dependent docker container by modifying the `docker-compose.yml` to expose the IPC socket as one of the `volumes` on the `worker` container:

```yml
  worker: &worker

    # ...

    volumes:
      - ~/.ethereum/rinkeby/geth.ipc:/root/.ethereum/rinkeby/geth.ipc
```

Then ensure the following is set in **config/settings/rinkeby.py**:

```
ETHEREUM_IPC_PATH = '/root/.ethereum/rinkeby/geth.ipc'
```

Edit **.env** file in the root of the project and change:

`DJANGO_SETTINGS_MODULE=config.settings.local` to `DJANGO_SETTINGS_MODULE=config.settings.rinkeby`

Then in *gnosisdb root folder*:

```
docker-compose build --force-rm
docker-compose run web sh
python manage.py migrate
python manage.py setup_tournament --start-block-number 2000000
exit
docker-compose up
```

The command `setup_tournament` will prepare the database and set up periodic tasks:
  - `--start-block-number` will, if specified, start GnosisDB processing at a specific block instead of all the way back at the genesis block. You should give it as late a block before tournament events start occurring as you can.
  - **Ethereum blockchain event listener** every 5 seconds (the main task of the application).
  - **Scoreboard calculation** every 10 minutes.
  - **Token issuance** every minute. Tokens will be issued in batches of 50 users (to prevent
  exceeding the block limitation). A flag will be set to prevent users from being issued again on next
  execution of the task.
  - **Token issuance flag clear**. Once a day the token issuance flag will be cleared so users will
  receive new tokens every day.

All these tasks can be changed in the [application admin](http://localhost:8000/admin/django_celery_beat/periodictask/).
You will need a superuser:

```
docker-compose run web sh
python manage.py createsuperuser
```

You should have now the api running in http://localhost:8000. You have to be patient because the
first synchronization of Rinkeby may take some time, depending on how many blocks GnosisDB has to process. It may take even more time if your Geth node is unsynchronized, since it [may need to finish synchronizing](https://github.com/ethereum/go-ethereum/issues/14338) before it will have the information required.

#### How to issue tournament tokens
GnosisDB comes with an handful command allowing to issue new tokens.

Go to gnosisdb/ root directory and execute:

```python manage.py issue_tournament_tokens address1,adress2,address3 amount```

as follows:

```python manage.py issue_tournament_tokens 0x0...a, 0x...b,0x...c 1000000000000000000```

where amount worth of 1000000000000000000 equals 1 token.


GNOSISDB DEPLOYMENT IN KUBERNETES
----------------------------------

### Requirements

There are a few necessary requirements:
  - Minimum Kubernetes version:  **1.9**
  - Ethereum network: **Rinkeby** (in the example)
    - If you want another network you must change the address:
      - Download https://github.com/gnosis/gnosis-contracts
      - Execute `truffle networks`
      - Replace the example addresses with this new ones in `gnosisdb-web-deployment.yaml`, `gnosisdb-worker-deployment.yaml` and `gnosisdb-scheduler-deployment.yaml` files

### Database
   ##### Database creation
   It is necessary to create a database so that GnosisDB could index blockchain events.

   GnosisDB is tested with **Postgres** database, if you want to use another database you will have to change the connection driver.
   ##### Database secret creation
   Set your database params.
  ```
  kubectl create secret generic gnosisdb-database \
  --from-literal host='[DATABASE_HOST]' \
  --from-literal name=[DATABASE_NAME] \
  --from-literal user=[DATABASE_USER] \
  --from-literal password='[DATABASE_PASSWORD]' \
  --from-literal port=[DATABASE_PORT]
  ```

### Persistent volume creation
It will be used for storing blockchain data of Geth node.

### Rabbit service
It is necessary for sending messages between gnosisdb scheduler and worker. Run rabbit service:

  ```
  kubectl apply -f rabbitmq-gnosisdb
  ```

### Gnosisdb services
##### Web
Set your custom environment variables in `gnosisdb-web-deployment.yaml`. You **only** have to set environment variables which have the `# CUSTOM` annotation.

##### Celery Scheduler
Set your custom environment variables in `gnosisdb-scheduler-deployment.yaml`. You **only** have to set environment variables which have the `# CUSTOM` annotation.

##### Celery Worker
  - Set your custom environment variables in `gnosisdb-worker-deployment.yaml`. You **only** have to set environment variables which have the `# CUSTOM` annotation.
  - Set persistent volume which was created in a previous step. Geth node uses it.

##### RUN services
After setting custom environments in the previous steps, application can be started. Apply to the folder `gnosisdb` the following command:
```
kubectl apply -f gnosisdb
```

### Celery task configuration
  - Create an admin user to access the /admin interface.
  ```
    kubectl exec -it [GNOSISDB_WEB_POD_NAME] -c web sh
    python manage.py createsuperuser
  ```
  - Login into the admin /interface with your admin user
  - Create celery periodic task (follow the paragraph where It is explained).


Contributors
------------
- Stefan George (stefan@gnosis.pm)
- Denís Graña (denis@gnosis.pm)
- Giacomo Licari (giacomo.licari@gnosis.pm)
- Uxío Fuentefría (uxio@gnosis.pm)
