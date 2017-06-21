from settings_utils.singleton import Singleton
from decoder import Decoder
from json import loads, dumps
from eth.web3_service import Web3Service
from django.conf import settings
from django.utils.module_loading import import_string
from celery.utils.log import get_task_logger
from eth.models import Daemon
from settings_utils.address_getter import addresses_getter
from ethereum.utils import remove_0x_head

logger = get_task_logger(__name__)


class UnknownBlock(Exception):
    pass


class EventListener(Singleton):

    def __init__(self, contract_map=settings.GNOSISDB_CONTRACTS):
        super(EventListener, self).__init__()
        self.decoder = Decoder()
        self.web3 = Web3Service().web3
        self.contract_map = contract_map

    def next_block(self):
        return Daemon.get_solo().block_number

    def update_and_next_block(self):
        daemon = Daemon.get_solo()
        current = self.web3.eth.blockNumber
        if daemon.block_number < current:
            blocks_to_update = range(daemon.block_number+1, current+1)
            # logger.info("block range {}-{} {}".format(daemon.block_number, current, blocks_to_update))
            daemon.block_number = current
            daemon.save()
            return blocks_to_update
        else:
            return []

    def get_logs(self, block_number):
        block = self.web3.eth.getBlock(block_number)
        logs = []

        if block and block.get(u'hash'):
            # logger.info('block hash {}'.format(block.get('hash')))
            for tx in block[u'transactions']:
                receipt = self.web3.eth.getTransactionReceipt(tx)
                # logger.info('receipt: {}'.format(dumps(receipt)))
                if receipt.get('logs'):
                    logs.extend(receipt[u'logs'])
            return logs, block
        else:
            raise UnknownBlock

    def execute(self):
        # update block number
        # get blocks and decode logs
        for block in self.update_and_next_block():
            # logger.info("block {}".format(block))

            # first get un-decoded logs and the block info
            logs, block_info = self.get_logs(block)

            ###########################
            # Decode logs #
            ###########################

            for contract in self.contract_map:
                # Add ABI
                self.decoder.add_abi(contract['EVENT_ABI'])

                # Get addresses watching
                addresses = None
                if contract.get('ADDRESSES'):
                    addresses = contract['ADDRESSES']
                elif contract.get('ADDRESSES_GETTER'):
                    try:
                        addresses = addresses_getter(str(contract['ADDRESSES_GETTER']))
                        logger.info('ADDRESS GETTER: {}'.format(addresses))
                    except Exception as e:
                        logger.error(e)
                        return

                # Filter logs by address and decode
                for log in logs:
                    logger.info('log_address {} {}'.format(remove_0x_head(log['address']), dumps(log)))
                    if remove_0x_head(log['address']) in addresses:
                        # try to decode it
                        decoded = self.decoder.decode_logs([log])

                        if decoded:
                            # save decoded event with event receiver
                            for log_json in decoded:
                                try:
                                    logger.info('LOG JSON: {}'.format(dumps(log_json)))
                                    logger.info('BLOCK JSON: {}'.format(dumps(block_info)))

                                    # load event receiver and save
                                    event_receiver = import_string(contract['EVENT_DATA_RECEIVER'])
                                    logger.info('EVENT RECEIVER: {}'.format(event_receiver))
                                    event_receiver().save(decoded_event=log_json, block_info=block_info)
                                except Exception as e:
                                    logger.error(e)