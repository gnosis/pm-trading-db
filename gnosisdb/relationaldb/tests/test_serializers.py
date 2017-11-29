from unittest import TestCase
from relationaldb.tests.factories import (
    CentralizedOracleFactory, EventFactory, MarketFactory, OutcomeTokenFactory, OutcomeTokenBalanceFactory,
    ScalarEventDescriptionFactory, CategoricalEventFactory, ScalarEventFactory, CategoricalEventDescriptionFactory
)
from relationaldb.serializers import (
    OutcomeTokenIssuanceSerializer, ScalarEventSerializer, OutcomeTokenRevocationSerializer,
    CategoricalEventSerializer, MarketSerializer, IPFSEventDescriptionDeserializer, CentralizedOracleSerializer,
    CentralizedOracleInstanceSerializer, OutcomeTokenInstanceSerializer, OutcomeTokenTransferSerializer
)

from relationaldb.models import OutcomeTokenBalance, OutcomeToken, ScalarEventDescription
from django.conf import settings
from ipfs.ipfs import Ipfs
from time import mktime


class TestSerializers(TestCase):

    def setUp(self):
        self.ipfs = Ipfs()

    def test_create_centralized_oracle(self):
        oracle = CentralizedOracleFactory()

        block = {
            'number': oracle.creation_block,
            'timestamp': mktime(oracle.creation_date_time.timetuple())
        }

        oracle_event = {
            'address': oracle.factory,
            'params': [
                {
                    'name': 'creator',
                    'value': oracle.creator
                },
                {
                    'name': 'centralizedOracle',
                    'value': oracle.address,
                },
                {
                    'name': 'ipfsHash',
                    'value': oracle.event_description.ipfs_hash[1:-7] + ''
                }
            ]
        }
        oracle.delete()
        s = CentralizedOracleSerializer(data=oracle_event, block=block)
        # ipfs_hash not saved to IPFS
        self.assertFalse(s.is_valid(), s.errors)
        # oracle.event_description
        event_description_json = {
            'title': oracle.event_description.title,
            'description': oracle.event_description.description,
            'resolutionDate': oracle.event_description.resolution_date.isoformat(),
            'outcomes': ['Yes', 'No']
        }

        # save event_description to IPFS
        ipfs_hash = self.ipfs.post(event_description_json)
        oracle_event.get('params')[2]['value'] = ipfs_hash

        s = CentralizedOracleSerializer(data=oracle_event, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)

    def test_create_centralized_oracle_scalar_event_with_outcomes(self):
        oracle = CentralizedOracleFactory()

        block = {
            'number': oracle.creation_block,
            'timestamp': mktime(oracle.creation_date_time.timetuple())
        }

        oracle_event = {
            'address': oracle.factory,
            'params': [
                {
                    'name': 'creator',
                    'value': oracle.creator
                },
                {
                    'name': 'centralizedOracle',
                    'value': oracle.address,
                },
                {
                    'name': 'ipfsHash',
                    'value': 'something unknown'
                }
            ]
        }
        # remove test oracle before creating it again
        oracle.delete()
        s = CentralizedOracleSerializer(data=oracle_event, block=block)
        # ipfs_hash not saved to IPFS
        self.assertFalse(s.is_valid(), s.errors)
        # oracle.event_description
        event_description_json = {
            'title': oracle.event_description.title,
            'description': oracle.event_description.description,
            'resolutionDate': oracle.event_description.resolution_date.isoformat(),
            'outcomes': [],
            'unit': 'unit',
            'decimals': 2
        }

        # save event_description to IPFS
        ipfs_hash = self.ipfs.post(event_description_json)
        oracle_event.get('params')[2]['value'] = ipfs_hash

        s = CentralizedOracleSerializer(data=oracle_event, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)

        self.assertEqual(ScalarEventDescription.objects.filter(ipfs_hash=instance.event_description.ipfs_hash).count(), 1)

    def test_event_description_different_outcomes(self):

        oracle = CentralizedOracleFactory()

        oracle.event_description.outcomes = ['Yes', 'No', 'Third']
        oracle.event_description.save()

        event = CategoricalEventFactory(oracle=oracle)

        # Categorical Event with different outcomes

        block = {
            'number': event.creation_block,
            'timestamp': mktime(event.creation_date_time.timetuple())
        }

        categorical_event = {
            'address': event.factory,
            'params': [
                {
                    'name': 'creator',
                    'value': event.creator
                },
                {
                    'name': 'collateralToken',
                    'value': event.creator
                },
                {
                    'name': 'oracle',
                    'value': oracle.address
                },
                {
                    'name': 'outcomeCount',
                    'value': 2
                },
                {
                    'name': 'categoricalEvent',
                    'value': event.address,
                }
            ]
        }

        event.delete()

        s = CategoricalEventSerializer(data=categorical_event, block=block)
        self.assertFalse(s.is_valid())
        categorical_event['params'][3]['value'] = 3
        s2 = CategoricalEventSerializer(data=categorical_event, block=block)
        self.assertTrue(s2.is_valid(), s.errors)
        instance = s2.save()
        self.assertIsNotNone(instance)

    def test_create_scalar_with_categorical_description(self):

        event_description = CategoricalEventDescriptionFactory()
        oracle = CentralizedOracleFactory(event_description=event_description)

        # Scalar Event with different outcomes
        event = ScalarEventFactory()

        block = {
            'number': event.creation_block,
            'timestamp': mktime(event.creation_date_time.timetuple())
        }

        scalar_event = {
            'address': event.factory,
            'params': [
                {
                    'name': 'creator',
                    'value': event.creator
                },
                {
                    'name': 'collateralToken',
                    'value': event.creator
                },
                {
                    'name': 'oracle',
                    'value': oracle.address
                },
                {
                    'name': 'upperBound',
                    'value': event.upper_bound
                },
                {
                    'name': 'lowerBound',
                    'value': event.lower_bound
                },
                {
                    'name': 'scalarEvent',
                    'value': event.address,
                }
            ]
        }

        event.delete()
        s = ScalarEventSerializer(data=scalar_event, block=block)
        self.assertFalse(s.is_valid())
        scalar_event['params'][3]['value'] = 3
        scalar_descripion = ScalarEventDescriptionFactory()
        oracle.event_description = scalar_descripion
        oracle.save()
        s2 = ScalarEventSerializer(data=scalar_event, block=block)
        self.assertTrue(s2.is_valid(), s.errors)
        instance = s2.save()
        self.assertIsNotNone(instance)

    def test_create_scalar_event(self):
        event = ScalarEventFactory()
        event_description = ScalarEventDescriptionFactory()
        oracle = CentralizedOracleFactory(event_description=event_description)

        block = {
            'number': event.creation_block,
            'timestamp': mktime(event.creation_date_time.timetuple())
        }

        scalar_event = {
            'address': event.factory,
            'params': [
                {
                    'name': 'creator',
                    'value': event.creator
                },
                {
                    'name': 'collateralToken',
                    'value': event.collateral_token
                },
                {
                    'name': 'oracle',
                    'value': oracle.address
                },
                {
                    'name': 'upperBound',
                    'value': 1
                },
                {
                    'name': 'lowerBound',
                    'value': 0
                }
            ]
        }
        event.delete()
        s = ScalarEventSerializer(data=scalar_event, block=block)
        self.assertFalse(s.is_valid(), s.errors)

        scalar_event.get('params').append({
            'name': 'scalarEvent',
            'value': event.address
        })

        s = ScalarEventSerializer(data=scalar_event, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)

    def test_create_categorical_event(self):
        event = CategoricalEventFactory()
        oracle = CentralizedOracleFactory()

        block = {
            'number': event.creation_block,
            'timestamp': mktime(event.creation_date_time.timetuple())
        }

        categorical_event = {
            'address': event.factory,
            'params': [
                {
                    'name': 'creator',
                    'value': event.creator
                },
                {
                    'name': 'collateralToken',
                    'value': event.collateral_token
                },
                {
                    'name': 'oracle',
                    'value': oracle.address
                },
                {
                    'name': 'outcomeCount',
                    'value': 2
                }
            ]
        }
        event.delete()
        s = CategoricalEventSerializer(data=categorical_event, block=block)
        self.assertFalse(s.is_valid(), s.errors)

        categorical_event.get('params').append({
            'name': 'categoricalEvent',
            'value': event.address
        })

        s = CategoricalEventSerializer(data=categorical_event, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)

    def test_create_market(self):
        oracle = CentralizedOracleFactory()
        event = CategoricalEventFactory(oracle=oracle)
        market = MarketFactory()

        block = {
            'number': market.creation_block,
            'timestamp': mktime(market.creation_date_time.timetuple())
        }

        market_dict = {
            'address': market.factory,
            'params': [
                {
                    'name': 'creator',
                    'value': market.creator
                },
                {
                    'name': 'centralizedOracle',
                    'value': oracle.address,
                },
                {
                    'name': 'marketMaker',
                    'value': market.market_maker
                },
                {
                    'name': 'fee',
                    'value': market.fee
                },
                {
                    'name': 'market',
                    'value': market.address
                }
            ]
        }
        market.delete()

        s = MarketSerializer(data=market_dict, block=block)
        self.assertFalse(s.is_valid(), s.errors)

        market_dict.get('params').append({
            'name': 'eventContract',
            'value': market.address
        })

        market_dict.get('params').append({
            'name': 'fee',
            'value': market.fee
        })

        s = MarketSerializer(data=market_dict, block=block)
        self.assertFalse(s.is_valid(), s.errors)

        market_dict.get('params')[-2]['value'] = event.address

        s = MarketSerializer(data=market_dict, block=block)
        self.assertFalse(s.is_valid(), s.errors)

        marketMaker = [x for x in market_dict.get('params') if x.get('name') == 'marketMaker'][0]
        marketMaker.update({'value': settings.LMSR_MARKET_MAKER})

        s = MarketSerializer(data=market_dict, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)

    def test_create_categorical_event_description(self):
        event_description = CategoricalEventDescriptionFactory()
        event_description.delete()
        categorical_event_description_json = {
            'title': event_description.title,
            'description': event_description.description,
            'resolution_date': event_description.resolution_date.isoformat(),
            'outcomes': event_description.outcomes
        }
        ipfs_hash = self.ipfs.post(categorical_event_description_json)
        serializer = IPFSEventDescriptionDeserializer(data={'ipfs_hash': ipfs_hash})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIsNotNone(serializer.save())

    def test_create_scalar_event_description(self):
        event_description = ScalarEventDescriptionFactory()
        event_description.delete()
        scalar_event_description_json = {
            'title': event_description.title,
            'description': event_description.description,
            'resolution_date': event_description.resolution_date.isoformat(),
            'unit': event_description.unit,
            'decimals': event_description.decimals,
        }
        ipfs_hash = self.ipfs.post(scalar_event_description_json)
        serializer = IPFSEventDescriptionDeserializer(data={'ipfs_hash': ipfs_hash})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIsNotNone(serializer.save())

    def test_create_centralized_oracle_instance(self):
        oracle = CentralizedOracleFactory()
        oracle.delete()
        # oracle.event_description
        event_description_json = {
            'title': oracle.event_description.title,
            'description': oracle.event_description.description,
            'resolutionDate': oracle.event_description.resolution_date.isoformat(),
            'outcomes': oracle.event_description.outcomes
        }

        block = {
            'number': oracle.creation_block,
            'timestamp': mktime(oracle.creation_date_time.timetuple())
        }

        oracle_event = {
            'address': oracle.factory,
            'params': [
                {
                    'name': 'creator',
                    'value': oracle.creator
                },
                {
                    'name': 'centralizedOracle',
                    'value': oracle.address,
                },
                {
                    'name': 'ipfsHash',
                    'value': oracle.event_description.ipfs_hash
                }
            ]
        }

        s = CentralizedOracleInstanceSerializer(data=oracle_event, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)

    def test_create_outcome_token_instance(self):
        outcome_token = OutcomeTokenFactory()
        event = ScalarEventFactory()

        outcome_token_event = {
            'address': event.address,
            'params': [
                {
                    'name': 'outcomeToken',
                    'value': outcome_token.address,
                },
                {
                    'name': 'index',
                    'value': outcome_token.index
                }
            ]
        }
        outcome_token.delete()

        s = OutcomeTokenInstanceSerializer(data=outcome_token_event)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)

    def test_issuance_outcome_token(self):
        outcome_token = OutcomeTokenFactory()
        event = EventFactory()

        issuance_event = {
            'name': 'Issuance',
            'address': outcome_token.address,
            'params': [
                {
                    'name': 'owner',
                    'value': event.address
                },
                {
                    'name': 'amount',
                    'value': 20,
                }
            ]
        }

        s = OutcomeTokenIssuanceSerializer(data=issuance_event)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()

        balance = OutcomeTokenBalance.objects.get(owner=event.address)
        self.assertEqual(balance.balance, 20)
        self.assertIsNotNone(instance)

        self.assertEqual(OutcomeToken.objects.get(address=outcome_token.address).total_supply,
                         outcome_token.total_supply + 20)

    def test_revocation_outcome_token(self):
        balance = OutcomeTokenBalanceFactory()
        balance.balance = 20
        balance.save()

        issuance_event = {
            'name': 'Revocation',
            'address': balance.outcome_token.address,
            'params': [
                {
                    'name': 'owner',
                    'value': balance.owner
                },
                {
                    'name': 'amount',
                    'value': 20,
                }
            ]
        }

        s = OutcomeTokenRevocationSerializer(data=issuance_event)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()

        self.assertEqual(OutcomeTokenBalance.objects.get(owner=balance.owner).balance, 0)
        self.assertIsNotNone(instance)

        self.assertEqual(OutcomeToken.objects.get(address=balance.outcome_token.address).total_supply,
                         balance.outcome_token.total_supply - 20)

    def test_transfer_outcome_token(self):
        outcome_token_balance = OutcomeTokenBalanceFactory()
        event = EventFactory()
        outcome_token_balance.balance = 20
        outcome_token_balance.save()

        transfer_event = {
            'name': 'Transfer',
            'address': outcome_token_balance.outcome_token.address,
            'params': [
                {
                    'name': 'from',
                    'value': outcome_token_balance.owner
                },
                {
                    'name': 'to',
                    'value': event.address
                },
                {
                    'name': 'value',
                    'value': outcome_token_balance.balance,
                }
            ]
        }

        s = OutcomeTokenTransferSerializer(data=transfer_event)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()

        self.assertEqual(OutcomeTokenBalance.objects.get(owner=outcome_token_balance.owner).balance, 0)
        self.assertIsNotNone(instance)
        self.assertEqual(instance.owner, event.address)
        self.assertEqual(instance.balance, 20)
