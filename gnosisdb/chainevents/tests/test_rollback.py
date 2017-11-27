# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.conf import settings
from chainevents.event_receivers import (
    CentralizedOracleFactoryReceiver, UltimateOracleFactoryReceiver, EventFactoryReceiver, MarketFactoryReceiver,
    CentralizedOracleInstanceReceiver, EventInstanceReceiver, UltimateOracleInstanceReceiver, OutcomeTokenInstanceReceiver,
    MarketInstanceReceiver
)

from relationaldb.models import (
    CentralizedOracle, UltimateOracle, ScalarEvent, CategoricalEvent, Market, OutcomeToken,
    Event, OutcomeVoteBalance, BuyOrder, SellOrder
)

from relationaldb.tests.factories import (
    UltimateOracleFactory, CentralizedOracleFactory,
    OracleFactory, EventFactory, MarketFactory, OutcomeTokenFactory,
    OutcomeVoteBalanceFactory, CategoricalEventFactory
)
from datetime import datetime
from time import mktime
from ipfs.ipfs import Ipfs


class TestRollabck(TestCase):

    def setUp(self):
        self.ipfs_api = Ipfs()

    def to_timestamp(self, datetime_instance):
        return mktime(datetime_instance.timetuple())

    def test_centralized_oracle_rollback(self):
        #===============================
        # Test oracle creation rollback
        #===============================
        oracle_one = CentralizedOracleFactory()

        # saving event_description to IPFS
        event_description_json = {
            'title':'Test title',
            'description': 'test long description',
            'resolutionDate': datetime.now().isoformat(),
            'outcomes': ['YES', 'NO']
        }

        ipfs_hash = self.ipfs_api.post(event_description_json)

        block = {
            'number': oracle_one.creation_block,
            'timestamp': self.to_timestamp(oracle_one.creation_date_time)
        }

        oracle_one_address = oracle_one.address[1:-7] + 'GIACOMO'

        oracle_one_event = {
            'address': oracle_one.factory[1:-7] + 'GIACOMO',
            'params': [
                {
                    'name': 'creator',
                    'value': oracle_one.creator
                },
                {
                    'name': 'centralizedOracle',
                    'value': oracle_one_address,
                },
                {
                    'name': 'ipfsHash',
                    'value': ipfs_hash
                }
            ]
        }

        CentralizedOracleFactoryReceiver().save(oracle_one_event, block)
        created_oracle = CentralizedOracle.objects.get(address=oracle_one_address)
        self.assertIsNotNone(created_oracle.pk)
        # Rollback
        CentralizedOracleFactoryReceiver().rollback(oracle_one_event, block)
        with self.assertRaises(CentralizedOracle.DoesNotExist):
            CentralizedOracle.objects.get(address=oracle_one_address)

        #===========================================
        # Test new oracle owner assignment rollback
        #===========================================

        # Create the oracle again
        oracle_two = CentralizedOracleFactory()
        # Test oracle owner assignment
        new_owner_address = oracle_two.address[0:-8] + 'GIACOMO2'
        change_owner_event = {
            'name': 'OwnerReplacement',
            'address': oracle_two.address,
            'params': [
                {
                    'name': 'newOwner',
                    'value': new_owner_address
                }
            ]
        }

        centralized_oracle_without_owner_replacement = CentralizedOracle.objects.get(address=oracle_two.address)
        # Change owner
        CentralizedOracleInstanceReceiver().save(change_owner_event)
        centralized_oracle_with_owner_replacement = CentralizedOracle.objects.get(address=oracle_two.address)
        self.assertEquals(centralized_oracle_with_owner_replacement.owner, new_owner_address)
        # Rollback
        CentralizedOracleInstanceReceiver().rollback(change_owner_event, block)
        centralized_oracle_with_owner_rollback = CentralizedOracle.objects.get(address=oracle_two.address)
        self.assertEquals(centralized_oracle_with_owner_rollback.owner, centralized_oracle_without_owner_replacement.owner)

        #===========================================
        # Test oracle outcome assignment rollback
        #===========================================

        outcome_assignment_event = {
            'name': 'OutcomeAssignment',
            'address': centralized_oracle_with_owner_rollback.address,
            'params': [{
                'name': 'outcome',
                'value': 1,
            }]
        }

        CentralizedOracleInstanceReceiver().save(outcome_assignment_event)
        centralized_oracle_with_outcome_assignment = CentralizedOracle.objects.get(address=centralized_oracle_with_owner_rollback.address)
        self.assertTrue(centralized_oracle_with_outcome_assignment.is_outcome_set)
        self.assertEqual(centralized_oracle_with_outcome_assignment.outcome, 1)
        CentralizedOracleInstanceReceiver().rollback(outcome_assignment_event, block)
        centralized_oracle_with_outcome_assignment_rollback = CentralizedOracle.objects.get(address=centralized_oracle_with_owner_rollback.address)
        self.assertFalse(centralized_oracle_with_outcome_assignment_rollback.is_outcome_set)
        self.assertIsNone(centralized_oracle_with_outcome_assignment_rollback.outcome)

    def test_scalar_event_rollback(self):
        oracle = OracleFactory()
        event = EventFactory()
        event_address = event.address[0:33] + 'GIACOMO'

        block = {
            'number': oracle.creation_block,
            'timestamp': self.to_timestamp(oracle.creation_date_time)
        }

        scalar_event = {
            'address': oracle.factory[0:33] + 'GIACOMO',
            'name': 'ScalarEventCreation',
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

        EventFactoryReceiver().save(scalar_event, block)
        event = ScalarEvent.objects.get(address=event_address)
        self.assertIsNotNone(event.pk)
        EventFactoryReceiver().rollback(scalar_event, block)
        with self.assertRaises(ScalarEvent.DoesNotExist):
            ScalarEvent.objects.get(address=event_address)

    def test_categorical_event_rollback(self):
        event = EventFactory()
        oracle = OracleFactory()
        event_address = event.address[0:33] + 'GIACOMO'

        block = {
            'number': oracle.creation_block,
            'timestamp': self.to_timestamp(oracle.creation_date_time)
        }

        categorical_event = {
            'address': oracle.factory[0:33] + 'GIACOMO',
            'name': 'CategoricalEventCreation',
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

        EventFactoryReceiver().save(categorical_event, block)
        event = CategoricalEvent.objects.get(address=event_address)
        self.assertIsNotNone(event.pk)
        EventFactoryReceiver().rollback(categorical_event, block)
        with self.assertRaises(CategoricalEvent.DoesNotExist):
            CategoricalEvent.objects.get(address=event_address)

    def test_market_rollback(self):
        oracle_factory = CentralizedOracleFactory()
        event_factory = CategoricalEventFactory(oracle=oracle_factory)
        market_factory = MarketFactory()

        block = {
            'number': oracle_factory.creation_block,
            'timestamp': self.to_timestamp(oracle_factory.creation_date_time)
        }

        market_creation_event = {
            'address': oracle_factory.factory[1:-7] + 'GIACOMO',
            'params': [
                {
                    'name': 'creator',
                    'value': oracle_factory.creator
                },
                {
                    'name': 'centralizedOracle',
                    'value': oracle_factory.address[1:-7] + 'GIACOMO',
                },
                {
                    'name': 'marketMaker',
                    'value': settings.LMSR_MARKET_MAKER
                },
                {
                    'name': 'fee',
                    'value': market_factory.fee
                },
                {
                    'name': 'eventContract',
                    'value': event_factory.address
                },
                {
                    'name': 'market',
                    'value': market_factory.address[0:7] + 'another'
                }
            ]
        }

        MarketFactoryReceiver().save(market_creation_event, block)
        market_without_rollback = Market.objects.get(event=event_factory.address)
        self.assertIsNotNone(market_without_rollback.pk)
        # Rollback
        MarketFactoryReceiver().rollback(market_creation_event, block)
        with self.assertRaises(Market.DoesNotExist):
            Market.objects.get(event=event_factory.address)

    def test_market_outcome_token_purchase_rollback(self):
        #===========================================
        # Test outcome token purchase
        #===========================================
        oracle_factory = CentralizedOracleFactory()
        event_factory = CategoricalEventFactory(oracle=oracle_factory)
        outcome_token = OutcomeTokenFactory(event=event_factory, index=0)
        market_without_rollback = MarketFactory(event=event_factory)
        buyer_address = '{:040d}'.format(100)
        self.assertIsNotNone(market_without_rollback.pk)

        block = {
            'number': oracle_factory.creation_block,
            'timestamp': self.to_timestamp(oracle_factory.creation_date_time)
        }

        outcome_token_purchase_event = {
            'name': 'OutcomeTokenPurchase',
            'address': market_without_rollback.address,
            'params': [
                {'name': 'outcomeTokenCost', 'value': 100},
                {'name': 'marketFees', 'value': 10},
                {'name': 'buyer', 'value': buyer_address},
                {'name': 'outcomeTokenIndex', 'value': 0},
                {'name': 'outcomeTokenCount', 'value': 10},
            ]
        }

        # Send outcome token purchase event
        MarketInstanceReceiver().save(outcome_token_purchase_event, block)
        orders_before_rollback = BuyOrder.objects.filter(
            creation_block=block.get('number'),
            sender=buyer_address,
            market=market_without_rollback
        )
        self.assertEquals(len(orders_before_rollback), 1)

        # Outcome token purchase rollback
        MarketInstanceReceiver().rollback(outcome_token_purchase_event, block)
        market_with_rollback = Market.objects.get(event=event_factory.address)
        orders_after_rollback = BuyOrder.objects.filter(
            creation_block=block.get('number'),
            sender=buyer_address,
            market=market_with_rollback
        )
        self.assertEquals(len(orders_after_rollback), 0)

    def test_market_outcome_token_sale_rollback(self):
        categorical_event = CategoricalEventFactory()
        outcome_token = OutcomeTokenFactory(event=categorical_event, index=0)
        market = MarketFactory(event=categorical_event)
        seller_address = '{:040d}'.format(100)

        block = {
            'number': 1,
            'timestamp': self.to_timestamp(datetime.now())
        }
        outcome_token_sell_event = {
            'name': 'OutcomeTokenSale',
            'address': market.address,
            'params': [
                {'name': 'outcomeTokenProfit', 'value': 100},
                {'name': 'marketFees', 'value': 10},
                {'name': 'seller', 'value': seller_address},
                {'name': 'outcomeTokenIndex', 'value': 0},
                {'name': 'outcomeTokenCount', 'value': 10},
            ]
        }

        MarketInstanceReceiver().save(outcome_token_sell_event, block)
        orders_before_rollback = SellOrder.objects.filter(
            creation_block=block.get('number'),
            sender=seller_address
        )
        self.assertEquals(len(orders_before_rollback), 1)

        # Outcome token sell rollback
        MarketInstanceReceiver().rollback(outcome_token_sell_event, block)
        orders_before_rollback = SellOrder.objects.filter(
            creation_block=block.get('number'),
            sender=seller_address
        )
        self.assertEquals(len(orders_before_rollback), 0)

    def test_market_outcome_token_shortsale_rollback(self):
        pass

    def test_market_funding_rollback(self):
        market_factory = MarketFactory()
        block = {
            'number': 1,
            'timestamp': self.to_timestamp(datetime.now())
        }
        market_funding_event = {
            'name': 'MarketFunding',
            'address': market_factory.address,
            'params': [
                {
                    'name': 'funding',
                    'value': 100
                }
            ]
        }

        MarketInstanceReceiver().save(market_funding_event)
        market_without_rollback = Market.objects.get(address=market_factory.address)
        self.assertEquals(market_without_rollback.stage, 1)
        self.assertEquals(market_without_rollback.funding, 100)
        # Rollback
        MarketInstanceReceiver().rollback(market_funding_event, block)
        market_with_rollback = Market.objects.get(address=market_factory.address)
        self.assertEquals(market_with_rollback.stage, 0)
        self.assertIsNone(market_with_rollback.funding)

    def test_market_closing_rollback(self):
        market_factory = MarketFactory()
        block = {
            'number': 1,
            'timestamp': self.to_timestamp(datetime.now())
        }
        market_closing_event = {
            'name': 'MarketClosing',
            'address': market_factory.address,
            'params': []
        }

        MarketInstanceReceiver().save(market_closing_event)
        market_without_rollback = Market.objects.get(address=market_factory.address)
        self.assertEquals(market_without_rollback.stage, 2)
        # Rollback
        MarketInstanceReceiver().rollback(market_closing_event, block)
        market_with_rollback = Market.objects.get(address=market_factory.address)
        self.assertEquals(market_with_rollback.stage, 1)

    def test_market_fee_withdrawal_rollback(self):
        market_factory = MarketFactory()
        block = {
            'number': 1,
            'timestamp': self.to_timestamp(datetime.now())
        }
        market_withdraw_event = {
            'name': 'FeeWithdrawal',
            'address': market_factory.address,
            'params': [
                {
                    'name': 'fees',
                    'value': 10
                }
            ]
        }

        MarketInstanceReceiver().save(market_withdraw_event)
        market_without_rollback = Market.objects.get(address=market_factory.address)
        self.assertEquals(market_without_rollback.withdrawn_fees, market_factory.withdrawn_fees+10)
        # Rollback
        MarketInstanceReceiver().rollback(market_withdraw_event, block)
        market_with_rollback = Market.objects.get(address=market_factory.address)
        self.assertEquals(market_with_rollback.withdrawn_fees, market_factory.withdrawn_fees)

        """MarketFactoryReceiver().save(market_creation_event, block)
        market_without_rollback = Market.objects.get(event=event_factory.address)
        self.assertIsNotNone(market_without_rollback.pk)

        outcome_assignment_event = {
            'name': 'OutcomeAssignment',
            'address': event_factory.address,
            'params': [{
                'name': 'outcome',
                'value': 1,
            }]
        }

        EventInstanceReceiver().save(outcome_assignment_event, block)
        event = Event.objects.get(address=event_factory.address)
        self.assertTrue(event.is_winning_outcome_set)

        # Rollback
        MarketInstanceReceiver().rollback(outcome_assignment_event, block)
        market_with_rollback = Market.objects.get(event=event_factory.address)
        orders_after_rollback = BuyOrder.objects.filter(
            creation_date_time=self.validated_data.get('creation_date_time'),
            creation_block=self.validated_data.get('creation_block'),
            sender=self.validated_data.get('buyer'),
            market=market_with_rollback
        )
        self.assertEquals(len(orders_after_rollback), 0)"""
