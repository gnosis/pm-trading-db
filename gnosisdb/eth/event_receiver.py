from abc import ABCMeta, abstractmethod
from serializers import CentralizedOracleSerializer, ScalarEventSerializer, CategoricalEventSerializer,\
    UltimateOracleSerializer, MarketSerializer


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