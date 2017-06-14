from abc import ABCMeta, abstractmethod
from relationaldb.serializers import CentralizedOracleSerializer, ScalarEventSerializer, CategoricalEventSerializer,\
    UltimateOracleSerializer, MarketSerializer

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class AbstractEventReceiver(object):
    """Abstract EventReceiver class."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def save(self, decoded_event, block_info): pass


class CentralizedOracleReceiver(AbstractEventReceiver):

    def save(self, decoded_event, block_info):
        logger.info("CentralizedOracleReceiver instantiating serializer")
        serializer = CentralizedOracleSerializer(data=decoded_event, block=block_info)
        logger.info("CentralizedOracleReceiver checking serializer is valid ...")
        if serializer.is_valid():
            logger.info("CentralizedOracleReceiver valid serialier")
            serializer.save()
            logger.info("CentralizedOracleReceiver instance saved")


class EventReceiver(AbstractEventReceiver):

    events = {
        'scalarEvent': ScalarEventSerializer,
        'categoricalEvent': CategoricalEventSerializer
    }

    def save(self, decoded_event, block_info):
        if self.events.get(decoded_event.get('name')):
            serializer = self.events.get(decoded_event.get('name'))(data=decoded_event, block=block_info)
            if serializer.is_valid():
                serializer.save()


class UltimateOracleReceiver(AbstractEventReceiver):

    def save(self, decoded_event, block_info):
        serializer = UltimateOracleSerializer(data=decoded_event, block=block_info)
        if serializer.is_valid():
            serializer.save()


class MarketReceiver(AbstractEventReceiver):
    def save(self, decoded_event, block_info):
        serializer = MarketSerializer(data=decoded_event, block=block_info)
        if serializer.is_valid():
            serializer.save()