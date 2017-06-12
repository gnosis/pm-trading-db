from unittest import TestCase
from relationaldb.factories import OracleFactory, CentralizedOracleFactory, UltimateOracleFactory, EventFactory
from relationaldb.serializers import (
    CentralizedOracleSerializer, EventSerializer, ScalarEventSerializer, UltimateOracleSerializer
)


class TestSerializers(TestCase):

    def test_deserialize_centralized_oracle(self):
        oracle = CentralizedOracleFactory()

        block = {
            'number': oracle.creation_block,
            'timestamp': oracle.creation_date
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

        block = {
            'number': oracle.creation_block,
            'timestamp': oracle.creation_date
        }

        oracle_event = {
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
                    'name': 'ipfsHash',
                    'value': oracle.event_description.ipfs_hash[1:-7] + ''
                }
            ]
        }

        s = CentralizedOracleSerializer(data=oracle_event, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)

    def test_deserialize_ultimate_oracle(self):
        forwarded_oracle = CentralizedOracleFactory()
        ultimate_oracle = UltimateOracleFactory()

        block = {
            'number': ultimate_oracle.creation_block,
            'timestamp': ultimate_oracle.creation_date
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

    def test_create_ultimate_oracle(self):
        forwarded_oracle = CentralizedOracleFactory()
        ultimate_oracle = UltimateOracleFactory()

        block = {
            'number': ultimate_oracle.creation_block,
            'timestamp': ultimate_oracle.creation_date
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
        pass
    
    def test_create_ultimate_oracle_no_collateral(self):
        pass

    def test_create_scalar_event(self):
        event_factory = EventFactory()
        oracle = OracleFactory()

        block = {
            'number': oracle.creation_block,
            'timestamp': oracle.creation_date
        }

        scalar_event = {
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
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)

