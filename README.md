
[![Coverage Status](https://coveralls.io/repos/github/gnosis/gnosisdb/badge.svg?branch=master)](https://coveralls.io/github/gnosis/gnosisdb?branch=master)

# GnosisDB
Gnosis Core Database Layer

Django Settings
-------

GnosisDB comes with a production settings file that you can edit.

##### ALLOWED_HOSTS
Specify the list of allowed hosts to connect to GnosisDB:

`ALLOWED_HOSTS = ['.gnosis.pm', '127.0.0.1', 'localhost']`

##### ADMINS
Specify your application administrators:

```
ADMINS = (
    ('Giacomo', 'giacomo.licari@gnosis.pm'),
    ('Denis', 'denis@gnosis.pm'),
    ('Stefan', 'stefan@gnosis.pm'),
)
```

##### ETHEREUM
Provide an Ethereum host, port and SSL (0, 1). Use SSL = 1 only if your Ethereum host supports https/SSL.

```
ETHEREUM_NODE_HOST = os.environ['ETHEREUM_NODE_HOST']
ETHEREUM_NODE_PORT = os.environ['ETHEREUM_NODE_PORT']
ETHEREUM_NODE_SSL = bool(int(os.environ['ETHEREUM_NODE_SSL']))
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
If you're willing to run RabbitMQ in a Dokku/Docker container, please read out [this link](https://github.com/dokku/dokku-rabbitmq).

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

`LSRM_MARKET_MAKER = '2f2be9db638cb31d4143cbc1525b0e104f7ed597'`

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

Installation
-------

### Install Docker and Docker Compose
* First, install docker: https://docs.docker.com/engine/installation/.
* Then, install docker compose: https://docs.docker.com/compose/install/
* Change your working directory: `cd gnosisdb`

### Build containers
The application is made up of several container images that are linked together using docker-compose. Before running the application, build the images:

`docker-compose build --force-rm`

### Create a Django superuser
Run the Web container with the following command and create a super user in order to access the /admin interface.

```
docker-compose run web bash
python gnosisdb/manage.py migrate
python gnosisdb/manage.py createsuperuser
```

### Run application
Start the gnosisdb server simply by bringing up the set of containers:

`sudo docker-compose up`

You can access it on http://localhost:8000 and the admin is on http://localhost:8000/admin

Development
-------
For development purposes you may want to run a Ganache node on your machine. To do so, run:

`ganache-cli --gasLimit 400000000 -d -h 0.0.0.0`

The -d option allows you to get the same address everytime a contract is deployed. You will not have to update your django settings everytime a new Ganache server is running.

The -h option tells Ganache to listen on all interfaces, including the bridge interfaces which are exposed inside of the docker containers. This will allow a setting of `ETHEREUM_NODE_HOST = '172.x.x.x'` to work for the Celery worker.

In another terminal instance, install `gnosis.js` (https://github.com/gnosis/gnosis.js) following the provided instructions. Go into that directory and deploy the contracts with:

`npm run migrate`

The execution will furnish all the contracts' addesses in the node_modules/@gnosis.pm/gnosis-core-contracts/build/contracts folder as parts of the build artifacts. You should also see the addresses displayed in your console.

You should verify that the addresses in ETH_EVENTS specified in /settings/base.py match what is displayed by the console for all the contracts including:

* Centralized Oracle Factory
* Event Factory
* Standard Market Factory
* Ultimate Oracle Factory

Run `docker-compose build` to apply the code changes and then `docker-compose up` to get GNOSISDB up and running.
Open your browser and go to http://localhost:8000/admin, provide your superuser username and password.
You should now see something like this:

![Admin overview](https://github.com/gnosis/gnosisdb/blob/master/img/django_admin_overview.png)

Create now a Celery periodic task.

![Periodic task management](https://github.com/gnosis/gnosisdb/blob/master/img/django_celery.png)

A test script was created on gnosis.js. This emulates the creation of oracles, events and markets.
Run it with:

`npm run test-gnosisdb`

How to implement your own AddressGetter and EventReceiver
-------
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
* ADDRESSES, the list of contract's addresses you may want to watch and listen to
* EVENT_ABI, the contract's JSON ABI in string format
* EVENT_DATA_RECEIVER, a custom event data receiver class
* NAME, the contract name
* PUBLISH, it denotes that this part of the config should have the addresses field in it published on that REST endpoint (see REST API paragraph)
* ADDRESSES_GETTER, a custom addresses getter class

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
* get_addresses(self), returns a list of strings (addresses)
* __contains__(self, address), returns True if the given address is in the addresses list, False otherwise

Take a look at ContractAddressGetter:

```
from relationaldb.models import Contract
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

`python gnosisdb/manage.py cleandatabase`

Then we must force the daemon to resync everything again:

`python gnosisdb/manage.py resync_daemon`

Contributors
------------
- Stefan George (stefan@gnosis.pm)
- Denís Graña (denis@gnosis.pm)
- Giacomo Licari (giacomo.licari@gnosis.pm)
