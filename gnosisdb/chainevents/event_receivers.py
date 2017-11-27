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


class CentralizedOracleFactoryReceiver(AbstractEventReceiver):

    def save(self, decoded_event, block_info):
        serializer = CentralizedOracleSerializer(data=decoded_event, block=block_info)
        if serializer.is_valid():
            serializer.save()
            logger.info('Centralized Oracle Factory Result Added: {}'.format(dumps(decoded_event)))
        else:
            logger.warning('INVALID Centralized Oracle Factory Result: {}'.format(dumps(decoded_event)))
            logger.warning(serializer.errors)

    def rollback(self, decoded_event, block_info):
        """
        A small trick is needed here. In order to re-use serializers and make them to be valid,
        (they would be invalid due to existing records on database), we 1st get the model instance and istantiate
        the serializer by passing also data and block values. By doing so the serializer will result
        valid.
        """
        instance = CentralizedOracle.objects.get(
            address=decoded_event.get('address')
        )
        serializer = CentralizedOracleSerializer(instance, data=decoded_event, block=block_info)
        if serializer.is_valid():
            serializer.rollback()
            logger.info('Centralized Oracle Factory Result reverted: {}'.format(dumps(decoded_event)))
        else:
            logger.warning('INVALID Centralized Oracle Factory Result for rollback: {}'.format(dumps(decoded_event)))
            logger.warning(serializer.errors)


class EventFactoryReceiver(AbstractEventReceiver):

    events = {
        'ScalarEventCreation': ScalarEventSerializer,
        'CategoricalEventCreation': CategoricalEventSerializer
    }

    def save(self, decoded_event, block_info):
        if self.events.get(decoded_event.get('name')):
            serializer = self.events.get(decoded_event.get('name'))(data=decoded_event, block=block_info)
            if serializer.is_valid():
                serializer.save()
                logger.info('Event Factory Result Added: {}'.format(dumps(decoded_event)))
            else:
                logger.warning('INVALID Event Factory Result: {}'.format(dumps(decoded_event)))
                logger.warning(serializer.errors)

    def rollback(self, decoded_event, block_info):
        serializer_class = self.events.get(decoded_event.get('name'))
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


class UltimateOracleFactoryReceiver(AbstractEventReceiver):

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


class MarketFactoryReceiver(AbstractEventReceiver):

    def save(self, decoded_event, block_info):
        serializer = MarketSerializer(data=decoded_event, block=block_info)
        if serializer.is_valid():
            serializer.save()
            logger.info('Market Factory Result Added: {}'.format(dumps(decoded_event)))
        else:
            logger.warning('INVALID Market Factory Result: {}'.format(dumps(decoded_event)))
            logger.warning(serializer.errors)

    def rollback(self, decoded_event, block_info):
        market_dict_parameter = filter(lambda x: x.get('name') == 'market', decoded_event.get('params'))[0]
        instance = Market.objects.get(
            address=market_dict_parameter.get('value')
        )
        serializer = MarketSerializer(instance, data=decoded_event, block=block_info)
        if serializer.is_valid():
            serializer.rollback()
            logger.info('Market Factory Result reverted: {}'.format(dumps(decoded_event)))
        else:
            logger.warning('INVALID Market Factory Result for rollback: {}'.format(dumps(decoded_event)))
            logger.warning(serializer.errors)


class MarketInstanceReceiver(AbstractEventReceiver):

    events = {
        'OutcomeTokenPurchase': OutcomeTokenPurchaseSerializer,
        'OutcomeTokenSale': OutcomeTokenSaleSerializer,
        'OutcomeTokenShortSale': OutcomeTokenShortSaleOrderSerializer,
        'MarketFunding': MarketFundingSerializer,
        'MarketClosing': MarketClosingSerializer,
        'FeeWithdrawal': FeeWithdrawalSerializer
    }

    def save(self, decoded_event, block_info=None):
        if block_info:
            serializer = self.events.get(decoded_event.get('name'))(data=decoded_event, block=block_info)
        else:
            serializer = self.events.get(decoded_event.get('name'))(data=decoded_event)

        if serializer.is_valid():
            serializer.save()
            logger.info('Market Instance Added: {}'.format(dumps(decoded_event)))
        else:
            logger.warning('INVALID Market Instance: {}'.format(dumps(decoded_event)))
            logger.warning(serializer.errors)

    def rollback(self, decoded_event, block_info):
        instance = None
        serializer_class = self.events.get(decoded_event.get('name'))

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


# contract instances
class CentralizedOracleInstanceReceiver(AbstractEventReceiver):

    events = {
        'OwnerReplacement': OwnerReplacementSerializer,
        'OutcomeAssignment': OutcomeAssignmentOracleSerializer
    }

    def save(self, decoded_event, block_info=None):
        if self.events.get(decoded_event.get('name')):
            if block_info:
                serializer = self.events.get(decoded_event.get('name'))(data=decoded_event, block=block_info)
            else:
                serializer = self.events.get(decoded_event.get('name'))(data=decoded_event)

            if serializer.is_valid():
                serializer.save()
                logger.info('Centralized Oracle Instance Added: {}'.format(dumps(decoded_event)))
            else:
                logger.warning('INVALID Centralized Oracle Instance: {}'.format(dumps(decoded_event)))
                logger.warning(serializer.errors)

    def rollback(self, decoded_event, block_info):
        serializer_class = self.events.get(decoded_event.get('name'))
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


class EventInstanceReceiver(AbstractEventReceiver):

    events = {
        'OutcomeTokenCreation': OutcomeTokenInstanceSerializer,
        'OutcomeAssignment': OutcomeAssignmentEventSerializer,
        'WinningsRedemption': WinningsRedemptionSerializer
    }

    def save(self, decoded_event, block_info=None):
        if self.events.get(decoded_event.get('name')):
            if block_info:
                serializer = self.events.get(decoded_event.get('name'))(data=decoded_event, block=block_info)
            else:
                serializer = self.events.get(decoded_event.get('name'))(data=decoded_event)

            if serializer.is_valid():
                serializer.save()
                logger.info('Event Instance Added: {}'.format(dumps(decoded_event)))
            else:
                logger.warning('INVALID Event Instance: {}'.format(dumps(decoded_event)))
                logger.warning(serializer.errors)

    def rollback(self, decoded_event, block_info):
        pass


class OutcomeTokenInstanceReceiver(AbstractEventReceiver):
    events = {
        'Issuance': OutcomeTokenIssuanceSerializer,  # sum to totalSupply, update data
        'Revocation': OutcomeTokenRevocationSerializer,  # subtract from total Supply, update data,
        'Transfer': OutcomeTokenTransferSerializer # moves balance between owners
    }

    def save(self, decoded_event, block_info=None):
        if self.events.get(decoded_event.get('name')):
            serializer = self.events.get(decoded_event.get('name'))(data=decoded_event)
            if serializer.is_valid():
                serializer.save()
            else:
                logger.warning(serializer.errors)

    def rollback(self, decoded_event, block_info):
        pass
