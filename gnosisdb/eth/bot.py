from utils import Singleton
from models import Daemon
from decoder import Decoder
from json import loads
from web3 import Web3, RPCProvider
from django.conf import settings
from django.apps import apps
from celery.utils.log import get_task_logger
from eth.models import Alert, Daemon


logger = get_task_logger(__name__)


class UnknownBlock(Exception):
    pass


class Bot(Singleton):

    def __init__(self):
        super(Bot, self).__init__()
        self.decoder = Decoder()
        self.web3 = Web3(
            RPCProvider(
                host=settings.ETHEREUM_NODE_HOST,
                port=settings.ETHEREUM_NODE_PORT,
                ssl=settings.ETHEREUM_NODE_SSL
            )
        )
        self.callback_per_block = getattr(settings, 'CALLBACK_PER_BLOCK', None)
        self.callback_per_exec = getattr(settings, 'CALLBACK_PER_EXEC', None)
        self.filter_logs = getattr(settings, 'LOG_FILTER_FUNCTION', None)

    def next_block(self):
        return Daemon.get_solo().block_number

    def update_block(self):
        daemon = Daemon.get_solo()
        current = self.web3.eth.blockNumber
        if daemon.block_number < current:
            blocks_to_update = range(daemon.block_number+1, current+1)
            logger.info("block range {}-{} {}".format(daemon.block_number, current, blocks_to_update))
            daemon.block_number = current
            daemon.save()
            return blocks_to_update
        else:
            return []

    # todo deprecated, remove
    def load_abis(self, contracts):
        alerts = Alert.objects.filter(contract__in=contracts)
        added = 0
        for alert in alerts:
            try:
                added += self.decoder.add_abi(loads(alert.abi))
            except ValueError:
                pass
        return added

    def get_logs(self, block_number):
        block = self.web3.eth.getBlock(block_number)
        logs = []
        if block and block.get(u'hash'):
            for tx in block[u'transactions']:
                receipt = self.web3.eth.getTransactionReceipt(tx)
                if receipt.get('logs'):
                    logs.extend(receipt[u'logs'])
            return logs, block
        else:
            raise UnknownBlock

    def execute(self):
        # update block number
        # get blocks and decode logs
        for block in self.update_block():
            logger.info("block {}".format(block))
            # first get un-decoded logs and the block info
            logs, block_info = self.get_logs(block)

            # 1st Decode factory logs

            # Get ABI's and contract addresses from settings
            factory_abis = [loads(x['abi']) for x in settings.GNOSISDB_FACTORIES]
            factory_addresses = [x[u'address'] for x in settings.GNOSISDB_FACTORIES]
            self.decoder.add_abi(factory_abis)

            # Filter by address and later try to decode
            factory_logs = []
            other_logs = []

            for log in logs:
                if log[u'address'] in factory_addresses:
                    factory_logs.extend(log)
                else:
                    other_logs.extend(log)

            decoded = self.decoder.decode_logs(factory_logs)

            # save factory logs (decoded ones) on database
            if decoded and len(decoded):
                # TODO, other module/function
                pass

            # 2nd Decode other logs (not triggered by factory contracts)
            # Get ABI's from settings
            other_abis = [loads(x['abi']) for x in settings.GNOSISDB_ABIS]
            self.decoder.add_abi(other_abis)

            # save factory logs (decoded ones) on database
            decoded = self.decoder.decode_logs(other_logs)
            if decoded and len(decoded):
                # TODO, other module/function
                pass