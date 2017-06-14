from utils import Singleton
from decoder import Decoder
from json import loads, dumps
from web3 import Web3, RPCProvider
from django.conf import settings
from celery.utils.log import get_task_logger
from eth.models import Daemon
import sys
from settings_utils.address_getter import addresses_getter

logger = get_task_logger(__name__)


class UnknownBlock(Exception):
    pass


class EventListener(Singleton):

    def __init__(self, rpc = None):
        super(EventListener, self).__init__()
        self.decoder = Decoder()
        self.web3 = Web3(
            rpc if rpc is not None else RPCProvider(
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
            logger.info('block hash {}'.format(block.get('hash')))
            for tx in block[u'transactions']:
                receipt = self.web3.eth.getTransactionReceipt(tx)
                logger.info('receipt: {}'.format(dumps(receipt)))
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
            # Decode logs #
            ###########################

            for contract in settings.GNOSISDB_CONTRACTS:
                # Add ABI
                self.decoder.add_abi(contract.EVENT_ABI)

                # Get addresses watching
                addresses = None
                if contract['ADDRESSES']:
                    addresses = contract['ADDRESSES']
                elif contract['ADDRESSES_GETTER']:
                    try:
                        addresses = addresses_getter(contract['ADDRESSES_GETTER'])
                    except Exception as e:
                        logger.info(e)
                        return

                # Filter logs by address and decode
                for log in logs:
                    if log['address'] in addresses:
                        # try to decode it
                        decoded = self.decoder.decode_logs([log])

                        if decoded:
                            # save decoded event with event receiver
                            for log_json in decoded:
                                try:
                                    logger.info('LOG JSON: {}'.format(dumps(log_json)))
                                    logger.info('BLOCK JSON: {}'.format(dumps(block_info)))

                                    # load event receiver and save
                                except Exception as e:
                                    logger.info(e)