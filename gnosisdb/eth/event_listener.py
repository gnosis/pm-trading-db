from settings_utils.singleton import Singleton
from decoder import Decoder
from json import loads, dumps
from eth.web3_service import Web3Service
from django.conf import settings
from django.utils.module_loading import import_string
from celery.utils.log import get_task_logger
from eth.models import Daemon
from ethereum.utils import remove_0x_head
from threading import RLock

logger = get_task_logger(__name__)


class UnknownBlock(Exception):
    pass


class EventListener(Singleton):

    def __init__(self, contract_map=settings.GNOSISDB_CONTRACTS):
        super(EventListener, self).__init__()
        self.decoder = Decoder()  # Decodes ethereum logs
        self.web3 = Web3Service().web3  # Gets transaction and block info from ethereum
        self.contract_map = contract_map  # Taken from settings, it's the contracts we listen to
        self.mutex = RLock()

    def get_logs(self, block_number):
        with self.mutex:
            return self.__get_logs(block_number)

    def execute(self):
        with self.mutex:
            return self.__execute()

    def next_block(self):
        with self.mutex:
            return self.__next_block()

    def update_and_next_block(self):
        with self.mutex:
            return self.__update_and_next_block()

    def __next_block(self):
        return Daemon.get_solo().block_number

    def __update_and_next_block(self):
        """
        Increases ethereum block saved on database to current one and returns the block numbers of
        blocks mined since last event_listener execution
        :return: [int]
        """
        daemon = Daemon.get_solo()
        current = self.web3.eth.blockNumber
        if daemon.block_number < current:
            blocks_to_update = range(daemon.block_number+1, current+1)
            daemon.block_number = current
            daemon.save()
            return blocks_to_update
        else:
            return []

    def __get_logs(self, block_number):
        """
        By a given block number returns a pair logs, block_info
        logs it's an array of decoded ethereum log dictionaries
        and block info it's a dic
        :param block_number:
        :return:
        """
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

    def __execute(self):
        # update block number
        # get blocks and decode logs
        for block in self.update_and_next_block():
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
                        addresses_getter = import_string(contract['ADDRESSES_GETTER'])
                        addresses = addresses_getter().get_addresses()
                    except Exception as e:
                        logger.error(e)
                        return

                # Filter logs by address and decode
                for log in logs:
                    if remove_0x_head(log['address']) in addresses:
                        # try to decode it
                        decoded = self.decoder.decode_logs([log])

                        if decoded:
                            # save decoded event with event receiver
                            for log_json in decoded:
                                try:
                                    # load event receiver and save
                                    event_receiver = import_string(contract['EVENT_DATA_RECEIVER'])
                                    # logger.info('EVENT RECEIVER: {}'.format(event_receiver))
                                    event_receiver().save(decoded_event=log_json, block_info=block_info)
                                except Exception as e:
                                    logger.error(e)
