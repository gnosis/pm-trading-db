from unittest import TestCase
from relationaldb.factories import (
    OracleFactory, CentralizedOracleFactory, UltimateOracleFactory, EventFactory,
    MarketFactory, EventDescriptionFactory, OutcomeTokenFactory
)
from relationaldb.serializers import (
    CentralizedOracleSerializer, EventSerializer, ScalarEventSerializer, UltimateOracleSerializer,
    CategoricalEventSerializer, MarketSerializer, IPFSEventDescriptionDeserializer,
    CentralizedOracleInstanceSerializer, OutcomeTokenInstanceSerializer
)

from ipfs.ipfs import Ipfs
from time import mktime


class TestSerializers(TestCase):

    def setUp(self):
        self.ipfs = Ipfs()
    """
    def test_deserialize_centralized_oracle(self):
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
                    'value': oracle.address
                },
                {
                    'name': 'ipfsHash',
                    'value': oracle.event_description.ipfs_hash
                }
            ]
        }

        s = CentralizedOracleSerializer(data=oracle_event, block=block)
        self.assertTrue(s.is_valid(), s.errors)

    def test_create_centralized_oracle(self):
        oracle = CentralizedOracleFactory()
        event_description_json = None

        block = {
            'number': oracle.creation_block,
            'timestamp': mktime(oracle.creation_date_time.timetuple())
        }

        oracle_event = {
            'address': oracle.factory[0:-7] + 'GIACOMO',
            'params': [
                {
                    'name': 'creator',
                    'value': oracle.creator
                },
                {
                    'name': 'centralizedOracle',
                    'value': oracle.address[1:-7] + 'GIACOMO',
                },
                {
                    'name': 'ipfsHash',
                    'value': oracle.event_description.ipfs_hash[1:-7] + ''
                }
            ]
        }

        s = CentralizedOracleSerializer(data=oracle_event, block=block)
        # ipfs_hash not saved to IPFS
        self.assertFalse(s.is_valid(), s.errors)
        # oracle.event_description
        event_description_json = {
            'title': oracle.event_description.title,
            'description': oracle.event_description.description,
            'resolution_date': oracle.event_description.resolution_date.isoformat(),
            'outcomes': ['Yes', 'No']
        }

        # save event_description to IPFS
        ipfs_hash = self.ipfs.post(event_description_json)
        oracle_event.get('params')[2]['value'] = ipfs_hash

        s = CentralizedOracleSerializer(data=oracle_event, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)

    def test_deserialize_ultimate_oracle(self):
        forwarded_oracle = CentralizedOracleFactory()
        ultimate_oracle = UltimateOracleFactory()

        block = {
            'number': ultimate_oracle.creation_block,
            'timestamp': mktime(ultimate_oracle.creation_date_time.timetuple())
        }

        oracle_event = {
            'address': ultimate_oracle.factory,
            'params': [
                {
                    'name': 'creator',
                    'value': ultimate_oracle.creator
                },
                {
                    'name': 'ultimateOracle',
                    'value': ultimate_oracle.address
                },
                {
                    'name': 'oracle',
                    'value': forwarded_oracle.address
                },
                {
                    'name': 'collateralToken',
                    'value': ultimate_oracle.collateral_token
                },
                {
                    'name': 'spreadMultiplier',
                    'value': ultimate_oracle.spread_multiplier
                },
                {
                    'name': 'challengePeriod',
                    'value': ultimate_oracle.challenge_period
                },
                {
                    'name': 'challengeAmount',
                    'value': ultimate_oracle.challenge_amount
                },
                {
                    'name': 'frontRunnerPeriod',
                    'value': ultimate_oracle.front_runner_period
                }
            ]
        }

        s = UltimateOracleSerializer(data=oracle_event, block=block)
        self.assertTrue(s.is_valid(), s.errors)
    """
    def test_create_ultimate_oracle(self):
        forwarded_oracle = CentralizedOracleFactory()
        ultimate_oracle = UltimateOracleFactory()

        block = {
            'number': ultimate_oracle.creation_block,
            'timestamp': mktime(ultimate_oracle.creation_date_time.timetuple())
        }

        oracle_event = {
            'address': ultimate_oracle.factory[0:7] + 'another',
            'params': [
                {
                    'name': 'creator',
                    'value': ultimate_oracle.creator
                },
                {
                    'name': 'ultimateOracle',
                    'value': ultimate_oracle.address[0:7] + 'another',
                },
                {
                    'name': 'oracle',
                    'value': forwarded_oracle.address
                },
                {
                    'name': 'collateralToken',
                    'value': ultimate_oracle.collateral_token
                },
                {
                    'name': 'spreadMultiplier',
                    'value': ultimate_oracle.spread_multiplier
                },
                {
                    'name': 'challengePeriod',
                    'value': ultimate_oracle.challenge_period
                },
                {
                    'name': 'challengeAmount',
                    'value': ultimate_oracle.challenge_amount
                },
                {
                    'name': 'frontRunnerPeriod',
                    'value': ultimate_oracle.front_runner_period
                }
            ]
        }

        s = UltimateOracleSerializer(data=oracle_event, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)
        self.assertIsNotNone(instance.pk)

    def test_create_ultimate_oracle_no_forwarded(self):
        forwarded_oracle = CentralizedOracleFactory()
        ultimate_oracle = UltimateOracleFactory()

        block = {
            'number': ultimate_oracle.creation_block,
            'timestamp': mktime(ultimate_oracle.creation_date_time.timetuple())
        }

        oracle_event = {
            'address': ultimate_oracle.factory[0:-8] + 'another',
            'params': [
                {
                    'name': 'creator',
                    'value': ultimate_oracle.creator
                },
                {
                    'name': 'ultimateOracle',
                    'value': ultimate_oracle.address[0:-8] + 'another',
                },
                {
                    'name': 'oracle',
                    'value': ultimate_oracle.forwarded_oracle.address[0:-5] + 'wrong'
                },
                {
                    'name': 'collateralToken',
                    'value': ultimate_oracle.collateral_token
                },
                {
                    'name': 'spreadMultiplier',
                    'value': ultimate_oracle.spread_multiplier
                },
                {
                    'name': 'challengePeriod',
                    'value': ultimate_oracle.challenge_period
                },
                {
                    'name': 'challengeAmount',
                    'value': ultimate_oracle.challenge_amount
                },
                {
                    'name': 'frontRunnerPeriod',
                    'value': ultimate_oracle.front_runner_period
                }
            ]
        }

        s = UltimateOracleSerializer(data=oracle_event, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)
        self.assertIsNotNone(instance.pk)
        self.assertIsNone(instance.forwarded_oracle)

    def test_create_scalar_event(self):
        event = EventFactory()
        oracle = OracleFactory()

        block = {
            'number': oracle.creation_block,
            'timestamp': mktime(oracle.creation_date_time.timetuple())
        }

        scalar_event = {
            'address': oracle.factory[1:-8] + 'GIACOMO1',
            'params': [
                {
                    'name': 'creator',
                    'value': oracle.creator
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
                    'value': 1
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

        s = ScalarEventSerializer(data=scalar_event, block=block)
        self.assertFalse(s.is_valid(), s.errors)

        scalar_event.get('params').append({
            'name': 'scalarEvent',
            'value': event.address[1:-8] + 'GIACOMO2'
        })

        s = ScalarEventSerializer(data=scalar_event, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)

    def test_create_categorical_event(self):
        event_factory = EventFactory()
        oracle = OracleFactory()

        block = {
            'number': oracle.creation_block,
            'timestamp': mktime(oracle.creation_date_time.timetuple())
        }

        categorical_event = {
            'address': oracle.factory[1:-7] + 'GIACOMO',
            'params': [
                {
                    'name': 'creator',
                    'value': oracle.creator
                },
                {
                    'name': 'collateralToken',
                    'value': event_factory.collateral_token
                },
                {
                    'name': 'oracle',
                    'value': oracle.address
                },
                {
                    'name': 'outcomeCount',
                    'value': 1
                }
            ]
        }

        s = CategoricalEventSerializer(data=categorical_event, block=block)
        self.assertFalse(s.is_valid(), s.errors)

        categorical_event.get('params').append({
            'name': 'categoricalEvent',
            'value': event_factory.address[1:-7] + 'GIACOMO'
        })

        s = CategoricalEventSerializer(data=categorical_event, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)

    def test_create_market(self):
        event_factory = EventFactory()
        market_factory = MarketFactory()
        oracle = OracleFactory()

        block = {
            'number': oracle.creation_block,
            'timestamp': mktime(oracle.creation_date_time.timetuple())
        }

        market_dict = {
            'address': oracle.factory[1:-7] + 'GIACOMO',
            'params': [
                {
                    'name': 'creator',
                    'value': oracle.creator
                },
                {
                    'name': 'centralizedOracle',
                    'value': oracle.address[1:-7] + 'GIACOMO',
                },
                {
                    'name': 'marketMaker',
                    'value': market_factory.market_maker
                },
                {
                    'name': 'fee',
                    'value': market_factory.fee
                },
                {
                    'name': 'market',
                    'value': market_factory.address[0:-7] + 'MARKET'
                }
            ]
        }

        s = MarketSerializer(data=market_dict, block=block)
        self.assertFalse(s.is_valid(), s.errors)

        market_dict.get('params').append({
            'name': 'eventContract',
            'value': event_factory.address[1:-9] + 'xGIACOMOx'
        })

        market_dict.get('params').append({
            'name': 'fee',
            'value': market_factory.fee
        })

        s = MarketSerializer(data=market_dict, block=block)
        self.assertFalse(s.is_valid(), s.errors)

        market_dict.get('params')[-2]['value'] = event_factory.address

        s = MarketSerializer(data=market_dict, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)

    def test_create_categorical_event_description(self):
        event_description_factory = EventDescriptionFactory()
        categorical_event_description_json = {
            'title': ' '.join(event_description_factory.title),
            'description': ' '.join(event_description_factory.description),
            'resolution_date': event_description_factory.resolution_date.isoformat(),
            'outcomes': ['A', 'B', 'C']
        }
        ipfs_hash = self.ipfs.post(categorical_event_description_json)
        serializer = IPFSEventDescriptionDeserializer(data={'ipfs_hash': ipfs_hash})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIsNotNone(serializer.save())

    def test_create_scalar_event_description(self):
        event_description_factory = EventDescriptionFactory()
        scalar_event_description_json = {
            'title': ' '.join(event_description_factory.title),
            'description': ' '.join(event_description_factory.description),
            'resolution_date': event_description_factory.resolution_date.isoformat(),
            'unit': 'X',
            'decimals': '4',
        }
        ipfs_hash = self.ipfs.post(scalar_event_description_json)
        serializer = IPFSEventDescriptionDeserializer(data={'ipfs_hash': ipfs_hash})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIsNotNone(serializer.save())

    def test_create_centralized_oracle_instance(self):
        oracle = CentralizedOracleFactory()
        # oracle.event_description
        event_description_json = {
            'title': oracle.event_description.title,
            'description': oracle.event_description.description,
            'resolution_date': oracle.event_description.resolution_date.isoformat(),
            'outcomes': ['Yes', 'No']
        }

        # save event_description to IPFS
        ipfs_hash = self.ipfs.post(event_description_json)

        block = {
            'number': oracle.creation_block,
            'timestamp': mktime(oracle.creation_date_time.timetuple())
        }

        oracle_event = {
            'address': oracle.factory[0:-7] + 'GIACOMO',
            'params': [
                {
                    'name': 'creator',
                    'value': oracle.address
                },
                {
                    'name': 'centralizedOracle',
                    'value': oracle.address[1:-8] + 'INSTANCE',
                },
                {
                    'name': 'ipfsHash',
                    'value': ipfs_hash
                }
            ]
        }

        s = CentralizedOracleInstanceSerializer(data=oracle_event, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)
    """
    def test_create_outcome_token_instance(self):
        outcome_token_factory = OutcomeTokenFactory()
        oracle_factory = OracleFactory()
        event_factory = EventFactory()
        event = None

        block = {
            'number': oracle_factory.creation_block,
            'timestamp': mktime(oracle_factory.creation_date_time.timetuple())
        }

        scalar_event = {
            'address': oracle_factory.factory[1:-12] + 'TESTINSTANCE',
            'params': [
                {
                    'name': 'creator',
                    'value': oracle_factory.creator
                },
                {
                    'name': 'collateralToken',
                    'value': event_factory.collateral_token
                },
                {
                    'name': 'oracle',
                    'value': oracle_factory.address
                },
                {
                    'name': 'outcomeCount',
                    'value': 1
                },
                {
                    'name': 'upperBound',
                    'value': 1
                },
                {
                    'name': 'lowerBound',
                    'value': 0
                },
                {
                    'name': 'scalarEvent',
                    'value': event_factory.address[1:-12] + 'TESTINSTANCE'
                }
            ]
        }

        s = ScalarEventSerializer(data=scalar_event, block=block)
        s.is_valid()
        event = s.save()

        block = {
            'number': oracle_factory.creation_block,
            'timestamp': mktime(oracle_factory.creation_date_time.timetuple())
        }

        oracle_event = {
            'address': oracle_factory.factory[0:-7] + 'GIACOMO',
            'params': [
                {
                    'name': 'creator',
                    'value': event.creator
                },
                {
                    'name': 'address',
                    'value': event.address
                },
                {
                    'name': 'outcomeToken',
                    'value': oracle_factory.address[1:-8] + 'INSTANCE',
                },
                {
                    'name': 'index',
                    'value': outcome_token_factory.index
                }
            ]
        }

        s = OutcomeTokenInstanceSerializer(data=oracle_event, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)
        """

