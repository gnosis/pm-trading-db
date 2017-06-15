from utils import Singleton
from web3 import Web3, RPCProvider
from django.conf import settings


class Web3Service(Singleton):
    def __init__(self):
        super(Web3Service, self).__init__()
        self.web3 = Web3(
            RPCProvider(
                host=settings.ETHEREUM_NODE_HOST,
                port=settings.ETHEREUM_NODE_PORT,
                ssl=settings.ETHEREUM_NODE_SSL
            )
        )