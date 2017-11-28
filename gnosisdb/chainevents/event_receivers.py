from django_eth_events.chainevents import AbstractEventReceiver
from relationaldb.serializers import (
    CentralizedOracleSerializer, ScalarEventSerializer, CategoricalEventSerializer,
    UltimateOracleSerializer, MarketSerializer, OutcomeTokenInstanceSerializer,
    OutcomeTokenRevocationSerializer, OutcomeAssignmentEventSerializer,
    WinningsRedemptionSerializer, OwnerReplacementSerializer, OutcomeTokenIssuanceSerializer,
    OutcomeAssignmentOracleSerializer, ForwardedOracleOutcomeAssignmentSerializer,
    OutcomeChallengeSerializer, OutcomeVoteSerializer, WithdrawalSerializer, OutcomeTokenTransferSerializer,
    OutcomeTokenPurchaseSerializer, OutcomeTokenSaleSerializer, OutcomeTokenShortSaleOrderSerializer,
    MarketFundingSerializer, MarketClosingSerializer, FeeWithdrawalSerializer
)
from relationaldb.models import (
    CentralizedOracle, Market
)

from celery.utils.log import get_task_logger
from json import dumps

logger = get_task_logger(__name__)


class SerializerEventReceiver(AbstractEventReceiver):

    class Meta:
        events = {}
        primary_key_name = 'address'

    def save(self, decoded_event, block_info=None):
        if self.Meta.events.get(decoded_event.get('name')):
            if block_info:
                serializer = self.Meta.events.get(decoded_event.get('name'))(data=decoded_event, block=block_info)
            else:
                serializer = self.Meta.events.get(decoded_event.get('name'))(data=decoded_event)
            if serializer.is_valid():
                serializer.save()
                logger.info('Event Receiver {} added: {}'.format(self.__class__.__name__, dumps(decoded_event)))
            else:
                logger.warning('INVALID Data for Event Receiver {} save: {}'.format(self.__class__.__name__,
                                                                                        dumps(decoded_event)))
                logger.warning(serializer.errors)

    def rollback(self, decoded_event, block_info):
        serializer_class = self.Meta.events.get(decoded_event.get('name'))
        if type(self.Meta.primary_key_name) is str:
            primary_key_name = self.Meta.primary_key_name
        else:
            primary_key_name = self.Meta.primary_key_name.get(decoded_event.get('name'))
        primary_key = filter(lambda x: x.get('name') == primary_key_name, decoded_event.get('params'))[0].get('value')
        instance = serializer_class.Meta.model.objects.get(
            address=primary_key
        )

        serializer = serializer_class(instance, data=decoded_event, block=block_info)
        if serializer.is_valid():
            serializer.rollback()
            logger.info('Event Receiver {} reverted: {}'.format(self.__class__.__name__, dumps(decoded_event)))
        else:
            logger.warning('INVALID Data for Event Receiver {} rollback: {}'.format(self.__class__.__name__, dumps(decoded_event)))
            logger.warning(serializer.errors)


class CentralizedOracleFactoryReceiver(SerializerEventReceiver):

    class Meta:
        events = {
            'CentralizedOracleCreation': CentralizedOracleSerializer
        }
        primary_key_name = 'centralizedOracle'


class EventFactoryReceiver(SerializerEventReceiver):

    class Meta:
        events = {
            'ScalarEventCreation': ScalarEventSerializer,
            'CategoricalEventCreation': CategoricalEventSerializer
        }
        primary_key_name = {
            'ScalarEventCreation': 'scalarEvent',
            'CategoricalEventCreation': 'categoricalEvent'
        }


class UltimateOracleFactoryReceiver(AbstractEventReceiver):
    # TODO deprecated class, REMOVE

    def save(self, decoded_event, block_info):
        serializer = UltimateOracleSerializer(data=decoded_event, block=block_info)
        if serializer.is_valid():
            serializer.save()
            logger.info('Ultimate Oracle Factory Result Added: {}'.format(dumps(decoded_event)))
        else:
            logger.warning('INVALID Ultimate Oracle Factory Result: {}'.format(dumps(decoded_event)))
            logger.warning(serializer.errors)

    def rollback(self, decoded_event, block_info):
        pass


class MarketFactoryReceiver(SerializerEventReceiver):

    class Meta:
        events = {
            'StandardMarketCreation': MarketSerializer
        }
        primary_key_name = 'market'


class MarketInstanceReceiver(SerializerEventReceiver):

    class Meta:
        events = {
            'OutcomeTokenPurchase': OutcomeTokenPurchaseSerializer,
            'OutcomeTokenSale': OutcomeTokenSaleSerializer,
            'OutcomeTokenShortSale': OutcomeTokenShortSaleOrderSerializer,
            'MarketFunding': MarketFundingSerializer,
            'MarketClosing': MarketClosingSerializer,
            'FeeWithdrawal': FeeWithdrawalSerializer
        }

    def rollback(self, decoded_event, block_info):
        instance = None
        serializer_class = self.Meta.events.get(decoded_event.get('name'))

        if issubclass(serializer_class.Meta.model, Market):
            instance = serializer_class.Meta.model.objects.get(
                address=decoded_event.get('address')
            )
        else:
            instance = serializer_class.Meta.model.objects.get(
                market=decoded_event.get('address')
            )

        serializer = serializer_class(instance, data=decoded_event, block=block_info)
        if serializer.is_valid():
            serializer.rollback()
            logger.info('Market Instance reverted: {}'.format(dumps(decoded_event)))
        else:
            logger.warning('INVALID Market Instance Result for rollback: {}'.format(dumps(decoded_event)))
            logger.warning(serializer.errors)


class CentralizedOracleInstanceReceiver(SerializerEventReceiver):

    class Meta:
        events = {
            'OwnerReplacement': OwnerReplacementSerializer,
            'OutcomeAssignment': OutcomeAssignmentOracleSerializer
        }

    def rollback(self, decoded_event, block_info):
        serializer_class = self.Meta.events.get(decoded_event.get('name'))
        instance = serializer_class.Meta.model.objects.get(
            address=decoded_event.get('address')
        )

        serializer = serializer_class(instance, data=decoded_event, block=block_info)
        if serializer.is_valid():
            serializer.rollback()
            logger.info('Event Factory Result reverted: {}'.format(dumps(decoded_event)))
        else:
            logger.warning('INVALID Event Factory Result for rollback: {}'.format(dumps(decoded_event)))
            logger.warning(serializer.errors)


class UltimateOracleInstanceReceiver(AbstractEventReceiver):
    # TODO deprectated class, remove
    events = {
        'ForwardedOracleOutcomeAssignment': ForwardedOracleOutcomeAssignmentSerializer,
        'OutcomeChallenge': OutcomeChallengeSerializer,
        'OutcomeVote': OutcomeVoteSerializer,
        'Withdrawal': WithdrawalSerializer
    }

    def save(self, decoded_event, block_info=None):
        if self.events.get(decoded_event.get('name')):
            if block_info:
                serializer = self.events.get(decoded_event.get('name'))(data=decoded_event, block=block_info)
            else:
                serializer = self.events.get(decoded_event.get('name'))(data=decoded_event)

            if serializer.is_valid():
                serializer.save()
                logger.info('Ultimate Oracle Factory Result Added: {}'.format(dumps(decoded_event)))
            else:
                logger.warning('INVALID Ultimate Oracle Factory Result: {}'.format(dumps(decoded_event)))
                logger.warning(serializer.errors)

    def rollback(self, decoded_event, block_info):
        pass


class EventInstanceReceiver(SerializerEventReceiver):
    class Meta:
        events = {
            'OutcomeTokenCreation': OutcomeTokenInstanceSerializer,
            'OutcomeAssignment': OutcomeAssignmentEventSerializer,
            'WinningsRedemption': WinningsRedemptionSerializer
        }

    def rollback(self, decoded_event, block_info):
        pass


class OutcomeTokenInstanceReceiver(SerializerEventReceiver):
    class Meta:
        events = {
            'Issuance': OutcomeTokenIssuanceSerializer,  # sum to totalSupply, update data
            'Revocation': OutcomeTokenRevocationSerializer,  # subtract from total Supply, update data,
            'Transfer': OutcomeTokenTransferSerializer # moves balance between owners
        }

    def rollback(self, decoded_event, block_info):
        pass
