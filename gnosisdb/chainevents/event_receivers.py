from django_eth_events.chainevents import AbstractEventReceiver
from relationaldb.serializers import (
    CentralizedOracleSerializer, ScalarEventSerializer, CategoricalEventSerializer,
    MarketSerializer, OutcomeTokenInstanceSerializer,
    OutcomeTokenRevocationSerializer, OutcomeAssignmentEventSerializer,
    WinningsRedemptionSerializer, OwnerReplacementSerializer, OutcomeTokenIssuanceSerializer,
    OutcomeAssignmentOracleSerializer, OutcomeTokenTransferSerializer,
    OutcomeTokenPurchaseSerializer, OutcomeTokenSaleSerializer, OutcomeTokenShortSaleOrderSerializer,
    MarketFundingSerializer, MarketClosingSerializer, FeeWithdrawalSerializer, TournamentParticipantSerializer,
    TournamentTokenIssuanceSerializer, TournamentTokenTransferSerializer
)
from relationaldb.models import (
    CentralizedOracle, Market
)

from relationaldb.models import TournamentParticipant

from celery.utils.log import get_task_logger
from json import dumps

logger = get_task_logger(__name__)


class SerializerEventReceiver(AbstractEventReceiver):

    class Meta:
        events = {}
        primary_key_name = 'address'

    def save(self, decoded_event, block_info=None):
        # Get serializer based on Event Name and saved serializers in Meta.events dictionary
        if self.Meta.events.get(decoded_event.get('name')):
            # Block info is optional, only models that inherit from ContractCreatedByFactory need it
            if block_info:
                serializer = self.Meta.events.get(decoded_event.get('name'))(data=decoded_event, block=block_info)
            else:
                serializer = self.Meta.events.get(decoded_event.get('name'))(data=decoded_event)

            # Only valid data goes forward, non valid data is logged
            if serializer.is_valid():
                instance = serializer.save()
                logger.info('Event Receiver {} added: {}'.format(self.__class__.__name__, dumps(decoded_event)))
                # serializer model instance is returned in order to django-eth-events know it was a valid event
                return instance
            else:
                logger.warning('INVALID Data for Event Receiver {} save: {}'.format(self.__class__.__name__,
                                                                                        dumps(decoded_event)))
                logger.warning(serializer.errors)

    def rollback(self, decoded_event, block_info):
        serializer_class = self.Meta.events.get(decoded_event.get('name'))
        # Get primary key name from Meta.primary_key_name, it can be the same for all Events (string) or different for
        # each one (dictionary)
        if type(self.Meta.primary_key_name) is str:
            primary_key_name = self.Meta.primary_key_name
        else:
            primary_key_name = self.Meta.primary_key_name.get(decoded_event.get('name'))
        primary_key = filter(lambda x: x.get('name') == primary_key_name, decoded_event.get('params'))[0].get('value')

        # Find instance to update/delete
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


class MarketFactoryReceiver(SerializerEventReceiver):

    class Meta:
        events = {
            'StandardMarketCreation': MarketSerializer
        }
        primary_key_name = 'market'


###########################
# Instance Event Receivers
###########################


class BaseInstanceEventReceiver(SerializerEventReceiver):
    """
    Instance Event receivers get the model instance in a different way, info is in the root object sometimes and others
    In the parameters, we overwrite this function
    """
    class Meta:
        events = {}
        primary_key_name = {}

    def rollback(self, decoded_event, block_info):
        serializer_class = self.Meta.events.get(decoded_event.get('name'))

        primary_key_name = self.Meta.primary_key_name.get(decoded_event.get('name'))
        if type(primary_key_name) is str:
            filter_dict = {primary_key_name: decoded_event.get('address')}
        else:
            filter_dict = {}
            for pk_model, pk_event in primary_key_name.iteritems():
                if pk_event == 'creation_block':
                    filter_dict[pk_model] = block_info['number']
                elif decoded_event.get(pk_event) is None:
                    filter_dict[pk_model] = filter(lambda x: x.get('name') == pk_event, decoded_event.get('params'))[0].get('value')
                else:
                    filter_dict[pk_model] = decoded_event.get(pk_event)

        instance = serializer_class.Meta.model.objects.get(
            **filter_dict
        )

        serializer = serializer_class(instance, data=decoded_event, block=block_info)
        if serializer.is_valid():
            serializer.rollback()
            logger.info('Event Receiver {} reverted: {}'.format(self.__class__.__name__, dumps(decoded_event)))
        else:
            logger.warning(
                'INVALID Data for Event Receiver {} rollback: {}'.format(self.__class__.__name__, dumps(decoded_event))
            )
            logger.warning(serializer.errors)


class MarketInstanceReceiver(BaseInstanceEventReceiver):

    class Meta:
        events = {
            'OutcomeTokenPurchase': OutcomeTokenPurchaseSerializer,
            'OutcomeTokenSale': OutcomeTokenSaleSerializer,
            'OutcomeTokenShortSale': OutcomeTokenShortSaleOrderSerializer,
            'MarketFunding': MarketFundingSerializer,
            'MarketClosing': MarketClosingSerializer,
            'FeeWithdrawal': FeeWithdrawalSerializer
        }

        primary_key_name = {
            'OutcomeTokenPurchase': {
                'market': 'address',
                'sender': 'buyer',
                'creation_block': 'creation_block'
            },
            'OutcomeTokenSale': {
                'market': 'address',
                'sender': 'seller',
                'creation_block': 'creation_block'
            },
            'OutcomeTokenShortSale': {
                'market': 'address',
                'sender': 'buyer',
                'creation_block': 'creation_block'
            },
            'MarketFunding': 'address',
            'MarketClosing': 'address',
            'FeeWithdrawal': 'address'
        }


class CentralizedOracleInstanceReceiver(BaseInstanceEventReceiver):

    class Meta:
        events = {
            'OwnerReplacement': OwnerReplacementSerializer,
            'OutcomeAssignment': OutcomeAssignmentOracleSerializer
        }
        primary_key_name = {
            'OwnerReplacement': 'address',
            'OutcomeAssignment': 'address'
        }


class EventInstanceReceiver(BaseInstanceEventReceiver):
    class Meta:
        events = {
            'OutcomeTokenCreation': OutcomeTokenInstanceSerializer,
            'OutcomeAssignment': OutcomeAssignmentEventSerializer,
            'WinningsRedemption': WinningsRedemptionSerializer
        }
        primary_key_name = {
            'OutcomeTokenCreation': {
                'address': 'outcomeToken'
            },
            'OutcomeAssignment': 'address',
            'WinningsRedemption': 'address'
        }


class OutcomeTokenInstanceReceiver(BaseInstanceEventReceiver):
    class Meta:
        events = {
            'Issuance': OutcomeTokenIssuanceSerializer,  # sum to totalSupply, update data
            'Revocation': OutcomeTokenRevocationSerializer,  # subtract from total Supply, update data,
            'Transfer': OutcomeTokenTransferSerializer # moves balance between owners
        }
        primary_key_name = {
            'Issuance': 'address',
            'Revocation': 'address',
            'Transfer': {
                'owner': 'from',
                'outcome_token': 'address'
            }
        }


# ============================== #
#     Uport event receivers
# ============================== #


class UportIdentityManagerReceiver(SerializerEventReceiver):
    class Meta:
        events = {
            'IdentityCreated': TournamentParticipantSerializer,
        }
        primary_key_name = {
            'IdentityCreated': 'identity'
        }


class TournamentTokenReceiver(BaseInstanceEventReceiver):
    class Meta:
        events = {
            'Issuance': TournamentTokenIssuanceSerializer,  # sum to participant balance
            'Transfer': TournamentTokenTransferSerializer
        }
        primary_key_name = {
            'Issuance': {
                'owner': 'address'
            },
            'Transfer': {
                'from_participant': 'owner',
                'to_participant': 'to'
            }
        }