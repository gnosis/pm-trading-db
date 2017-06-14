from utils import Singleton
from decoder import Decoder
from json import loads, dumps
from web3 import Web3, RPCProvider
from django.conf import settings
from celery.utils.log import get_task_logger
from eth.models import Daemon
import sys

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

    def __load_file(self, import_name, silent=False):
        """Imports an object based on a string.  This is useful if you want to
        use import paths as endpoints or something similar.  An import path can
        be specified either in dotted notation (``xml.sax.saxutils.escape``)
        or with a colon as object delimiter (``xml.sax.saxutils:escape``).
        If `silent` is True the return value will be `None` if the import fails.
        :param import_name: the dotted name for the object to import.
        :param silent: if set to `True` import errors are ignored and
                       `None` is returned instead.
        :return: imported object
        """
        # force the import name to automatically convert to strings
        # __import__ is not able to handle unicode strings in the fromlist
        # if the module is a package
        import_name = str(import_name).replace(':', '.')
        try:
            try:
                __import__(import_name)
            except ImportError:
                if '.' not in import_name:
                    raise
            else:
                return sys.modules[import_name]
            module_name, obj_name = import_name.rsplit('.', 1)
            try:
                module = __import__(module_name, None, None, [obj_name])
            except ImportError:
                # support importing modules not yet set up by the parent module
                # (or package for that matter)
                module = self.__load_file(module_name)
            try:
                return getattr(module, obj_name)
            except AttributeError as e:
                raise ImportError(e)
        except ImportError as e:
            if not silent:
                raise Exception(sys.exc_info()[2])

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
            # logger.info('block has {} logs'.format(len(logs)))
            for log in logs:
                # Get ABI's and contract addresses from settings
                factory = settings.GNOSISDB_CONTRACTS.get(self.decoder.remove_prefix(log[u'address']))
                if factory:
                    # add factory abi to decoder
                    self.decoder.add_abi(loads(factory['factoryEventABI']))

                    # try to decode log
                    decoded = self.decoder.decode_logs([log])
                    if decoded:
                        # save decoded events if valid
                        for log_json in decoded:
                            try:
                                logger.info('LOG JSON: {}'.format(dumps(log_json)))
                                logger.info('BLOCK JSON: {}'.format(dumps(block_info)))
                                s_class = self.__load_file(factory['factoryEventSerializer'])
                                # logger.info('serializer class {}'.format(s_class))
                                s = s_class(data=log_json, block=block_info)
                                # logger.info('serializer instance {}'.format(s))
                                logger.info('serializer is_valid? {}'.format(s.is_valid()))
                                if s.is_valid():
                                    s.save()
                                else:
                                    logger.info('errors {}'.format(s.errors))
                            except Exception as e:
                                logger.info(e)
                else:
                    other_logs.append(log)

            # 2nd Decode Instance logs
            # todo