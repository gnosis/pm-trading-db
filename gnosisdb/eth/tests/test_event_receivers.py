# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from json import loads
from eth.event_receiver import (
    CentralizedOracleReceiver, UltimateOracleReceiver, EventReceiver, MarketReceiver
)

from relationaldb.models import (
    CentralizedOracle, UltimateOracle, ScalarEvent, CategoricalEvent, Market
)

from relationaldb.factories import (
    UltimateOracleFactory, CentralizedOracleFactory, CategoricalEventFactory,
    OracleFactory, EventFactory, MarketFactory
)
from datetime import datetime
from time import mktime
from ipfs.ipfs import Ipfs


class TestEventReceiver(TestCase):

    def setUp(self):
        self.ipfs_api = Ipfs()

    def to_timestamp(self, datetime_instance):
        return mktime(datetime_instance.timetuple())

    def test_centralized_oracle_receiver(self):
        oracle = CentralizedOracleFactory()
        # saving event_description to IPFS
        event_description_json = {
            'title':'Test title',
            'description': 'test long description',
            'resolution_date': datetime.now().isoformat(),
            'outcomes': ['YES', 'NO']
        }

        ipfs_hash = self.ipfs_api.post(event_description_json)

        block = {
            'number': oracle.creation_block,
            'timestamp': self.to_timestamp(oracle.creation_date)
        }

        oracle_address = oracle.address[1:-7] + 'GIACOMO'

        oracle_event = {
            'address': oracle.factory[1:-7] + 'GIACOMO',
            'params': [
                {
                    'name': 'creator',
                    'value': oracle.creator
                },
                {
                    'name': 'centralizedOracle',
                    'value': oracle_address,
                },
                {
                    'name': 'ipfsHash',
                    'value': ipfs_hash
                }
            ]
        }

        CentralizedOracleReceiver().save(oracle_event, block)
        created_oracle = CentralizedOracle.objects.get(address=oracle_address)
        self.assertIsNotNone(created_oracle.pk)

    def test_ultimate_oracle_receiver(self):
        oracle = UltimateOracleFactory()

        block = {
            'number': oracle.creation_block,
            'timestamp': self.to_timestamp(oracle.creation_date)
        }

        oracle_address = oracle.address[0:33] + 'GIACOMO'

        oracle_event = {
            'address': oracle.factory,
            'params': [
                {
                    'name': 'creator',
                    'value': oracle.creator
                },
                {
                    'name': 'ultimateOracle',
                    'value': oracle_address
                },
                {
                    'name': 'oracle',
                    'value': oracle_address
                },
                {
                    'name': 'collateralToken',
                    'value': oracle.collateral_token
                },
                {
                    'name': 'spreadMultiplier',
                    'value': oracle.spread_multiplier
                },
                {
                    'name': 'challengePeriod',
                    'value': oracle.challenge_period
                },
                {
                    'name': 'challengeAmount',
                    'value': oracle.challenge_amount
                },
                {
                    'name': 'frontRunnerPeriod',
                    'value': oracle.front_runner_period
                }
            ]
        }

        UltimateOracleReceiver().save(oracle_event, block)
        created_oracle = UltimateOracle.objects.get(address=oracle_address)
        self.assertIsNotNone(created_oracle.pk)

    def test_scalar_event_receiver(self):
        oracle = OracleFactory()
        event = EventFactory()
        event_address = event.address[0:33] + 'GIACOMO'

        block = {
            'number': oracle.creation_block,
            'timestamp': self.to_timestamp(oracle.creation_date)
        }

        scalar_event = {
            'address': oracle.factory[0:33] + 'GIACOMO',
            'name': 'scalarEvent',
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
                },
                {
                    'name': 'scalarEvent',
                    'value': event_address
                }
            ]
        }

        EventReceiver().save(scalar_event, block)
        event = ScalarEvent.objects.get(address=event_address)
        self.assertIsNotNone(event.pk)

    def test_categorical_event_receiver(self):
        event = EventFactory()
        oracle = OracleFactory()
        event_address = event.address[0:33] + 'GIACOMO'

        block = {
            'number': oracle.creation_block,
            'timestamp': self.to_timestamp(oracle.creation_date)
        }

        categorical_event = {
            'address': oracle.factory[0:33] + 'GIACOMO',
            'name': 'categoricalEvent',
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
                    'name': 'categoricalEvent',
                    'value': event_address
                }
            ]
        }

        EventReceiver().save(categorical_event, block)
        event = CategoricalEvent.objects.get(address=event_address)
        self.assertIsNotNone(event.pk)

    def test_market_receiver(self):
        event = EventFactory()
        market = MarketFactory()
        oracle = OracleFactory()
        event_address = event.address

        block = {
            'number': oracle.creation_block,
            'timestamp': self.to_timestamp(oracle.creation_date)
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
                    'value': market.market_maker
                },
                {
                    'name': 'fee',
                    'value': market.fee
                },
                {
                    'name': 'eventContract',
                    'value': event_address
                },
                {
                    'name': 'fee',
                    'value': market.fee
                }
            ]
        }

        MarketReceiver().save(market_dict, block)
        market = Market.objects.get(event=event_address)
        self.assertIsNotNone(market.pk)
        