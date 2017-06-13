from utils import Singleton
from relationaldb.models import CentralizedOracle
from decoder import Decoder
from json import loads
from web3 import Web3, RPCProvider
from django.conf import settings
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

    def update_and_next_block(self):
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
        for block in self.update_and_next_block():
            logger.info("block {}".format(block))

            # first get un-decoded logs and the block info
            logs, block_info = self.get_logs(block)

            ###########################
            # 1st Decode factory logs #
            ###########################

            # Decode factory logs
            other_logs = []
            for log in logs:
                # Get ABI's and contract addresses from settings
                factory = settings.GNOSISDB_CONTRACTS.get(log[u'address'])
                if factory:
                    # add factory abi to decoder
                    self.decoder.add_abi(loads(factory['factoryEventABI']))

                    # try to decode log
                    decoded = self.decoder.decode_logs([log])

                    if decoded:
                        # save decoded events if valid
                        for log_json in decoded:
                            s_class = __import__(factory['factorySerializer'])
                            s = s_class(data=log_json, block=block_info)
                            if s.is_valid():
                                s.save()
                else:
                    other_logs.append(log)

            # 2nd Decode Instance logs
            # todo