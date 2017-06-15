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
        serializer = CentralizedOracleSerializer(data=decoded_event, block=block_info)
        if serializer.is_valid():
            serializer.save()


class EventReceiver(AbstractEventReceiver):

    events = {
        'ScalarEventCreation': ScalarEventSerializer,
        'CategoricalEventCreation': CategoricalEventSerializer
    }

    def save(self, decoded_event, block_info):
        from json import dumps
        logger.info('Event Factory Serializer {}'.format(dumps(decoded_event)))
        if self.events.get(decoded_event.get('name')):
            serializer = self.events.get(decoded_event.get('name'))(data=decoded_event, block=block_info)
            if serializer.is_valid():
                serializer.save()
            else:
                logger.info(serializer.errors)


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