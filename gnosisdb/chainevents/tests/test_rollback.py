# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.conf import settings
from chainevents.event_receivers import (
    CentralizedOracleFactoryReceiver, EventFactoryReceiver, MarketFactoryReceiver,
    CentralizedOracleInstanceReceiver, EventInstanceReceiver, OutcomeTokenInstanceReceiver,
    MarketInstanceReceiver
)

from relationaldb.models import (
    CentralizedOracle, ScalarEvent, CategoricalEvent, Market, OutcomeToken,
    OutcomeTokenBalance, BuyOrder, SellOrder
)

from relationaldb.tests.factories import (
    CentralizedOracleFactory, OracleFactory, EventFactory, MarketFactory,
    OutcomeTokenFactory, CategoricalEventFactory, ScalarEventFactory
)
from datetime import datetime
from time import mktime
from ipfs.ipfs import Ipfs


class TestRollabck(TestCase):

    def setUp(self):
        self.ipfs_api = Ipfs()

    def to_timestamp(self, datetime_instance):
        return mktime(datetime_instance.timetuple())

    def test_centralized_oracle_factory_rollback(self):
        oracle = CentralizedOracleFactory()

        # saving event_description to IPFS
        event_description_json = {
            'title': oracle.event_description.title,
            'description': oracle.event_description.description,
            'resolutionDate': oracle.event_description.resolution_date.isoformat(),
            'outcomes': oracle.event_description.outcomes
        }

        ipfs_hash = self.ipfs_api.post(event_description_json)

        block = {
            'number': oracle.creation_block,
            'timestamp': self.to_timestamp(oracle.creation_date_time)
        }

        oracle_address = oracle.address

        oracle_event = {
            'name': 'CentralizedOracleCreation',
            'address': oracle.factory,
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
        oracle.delete()

        CentralizedOracleFactoryReceiver().save(oracle_event, block)
        created_oracle = CentralizedOracle.objects.get(address=oracle_address)
        self.assertIsNotNone(created_oracle.pk)
        # Rollback
        CentralizedOracleFactoryReceiver().rollback(oracle_event, block)
        with self.assertRaises(CentralizedOracle.DoesNotExist):
            CentralizedOracle.objects.get(address=oracle_address)

        # Rollback over nonexistent centralized oracle should fail
        self.assertRaises(Exception, CentralizedOracleFactoryReceiver().rollback, oracle_event, block)

    def test_oracle_owner_replacement_rollback(self):
        # Create the oracle
        oracle = CentralizedOracleFactory()
        oracle2 = CentralizedOracleFactory()
        new_owner_address = oracle2.creator
        block = {
            'number': 1,
            'timestamp': self.to_timestamp(datetime.now())
        }
        change_owner_event = {
            'name': 'OwnerReplacement',
            'address': oracle.address,
            'params': [
                {
                    'name': 'newOwner',
                    'value': new_owner_address
                }
            ]
        }

        centralized_oracle_without_owner_replacement = CentralizedOracle.objects.get(address=oracle.address)
        # Change owner
        CentralizedOracleInstanceReceiver().save(change_owner_event)
        centralized_oracle_with_owner_replacement = CentralizedOracle.objects.get(address=oracle.address)
        self.assertEquals(centralized_oracle_with_owner_replacement.owner, new_owner_address)
        # Rollback
        CentralizedOracleInstanceReceiver().rollback(change_owner_event, block)
        centralized_oracle_with_owner_rollback = CentralizedOracle.objects.get(address=oracle.address)
        self.assertEquals(centralized_oracle_with_owner_rollback.owner, centralized_oracle_without_owner_replacement.owner)

    def test_oracle_outcome_assignment_rollback(self):
        # Create the oracle
        oracle_factory = CentralizedOracleFactory()
        block = {
            'number': 1,
            'timestamp': self.to_timestamp(datetime.now())
        }
        outcome_assignment_event = {
            'name': 'OutcomeAssignment',
            'address': oracle_factory.address,
            'params': [{
                'name': 'outcome',
                'value': 1,
            }]
        }

        CentralizedOracleInstanceReceiver().save(outcome_assignment_event)
        centralized_oracle_with_outcome_assignment = CentralizedOracle.objects.get(address=oracle_factory.address)
        self.assertTrue(centralized_oracle_with_outcome_assignment.is_outcome_set)
        self.assertEqual(centralized_oracle_with_outcome_assignment.outcome, 1)
        CentralizedOracleInstanceReceiver().rollback(outcome_assignment_event, block)
        centralized_oracle_with_outcome_assignment_rollback = CentralizedOracle.objects.get(address=oracle_factory.address)
        self.assertFalse(centralized_oracle_with_outcome_assignment_rollback.is_outcome_set)
        self.assertIsNone(centralized_oracle_with_outcome_assignment_rollback.outcome)

    def test_scalar_event_factory_rollback(self):
        oracle = OracleFactory()
        event = ScalarEventFactory()
        event_address = event.address

        block = {
            'number': event.creation_block,
            'timestamp': self.to_timestamp(event.creation_date_time)
        }

        scalar_event = {
            'address': event.factory,
            'name': 'ScalarEventCreation',
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
                    'value': event_address
                }
            ]
        }
        event.delete()

        EventFactoryReceiver().save(scalar_event, block)
        event = ScalarEvent.objects.get(address=event_address)
        self.assertIsNotNone(event.pk)
        EventFactoryReceiver().rollback(scalar_event, block)
        with self.assertRaises(ScalarEvent.DoesNotExist):
            ScalarEvent.objects.get(address=event_address)

        # Rollback over an nonexistent event should fail
        self.assertRaises(Exception, EventFactoryReceiver().rollback, scalar_event, block)

    def test_categorical_event_factory_rollback(self):
        event = CategoricalEventFactory()
        oracle = OracleFactory()
        event_address = event.address

        block = {
            'number': event.creation_block,
            'timestamp': self.to_timestamp(event.creation_date_time)
        }

        categorical_event = {
            'address': event.factory,
            'name': 'CategoricalEventCreation',
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

        # Rollback over an nonexistent event shoul fail
        self.assertRaises(Exception, EventFactoryReceiver().rollback, categorical_event, block)

    def test_market_factory_rollback(self):
        oracle = CentralizedOracleFactory()
        event = CategoricalEventFactory(oracle=oracle)
        market = MarketFactory()

        block = {
            'number': oracle.creation_block,
            'timestamp': self.to_timestamp(oracle.creation_date_time)
        }

        market_creation_event = {
            'name': 'StandardMarketCreation',
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
                    'value': settings.LMSR_MARKET_MAKER
                },
                {
                    'name': 'fee',
                    'value': market.fee
                },
                {
                    'name': 'eventContract',
                    'value': event.address
                },
                {
                    'name': 'market',
                    'value': market.address
                }
            ]
        }
        market.delete()

        MarketFactoryReceiver().save(market_creation_event, block)
        market_without_rollback = Market.objects.get(event=event.address)
        self.assertIsNotNone(market_without_rollback.pk)
        # Rollback
        MarketFactoryReceiver().rollback(market_creation_event, block)
        with self.assertRaises(Market.DoesNotExist):
            Market.objects.get(event=event.address)

    def test_market_outcome_token_purchase_rollback(self):
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

    def test_outcome_token_transfer_rollback(self):
        outcome_token_factory = OutcomeTokenFactory()
        owner_one = outcome_token_factory.address[0:-5] + 'other'
        owner_two = outcome_token_factory.address[0:-2] + 'to'
        block = {
            'number': 1,
            'timestamp': self.to_timestamp(datetime.now())
        }
        issuance_event = {
            'name': 'Issuance',
            'address': outcome_token_factory.address,
            'params': [
                {
                    'name': 'owner',
                    'value': owner_one
                },
                {
                    'name': 'amount',
                    'value': 1000
                }
            ]
        }
        transfer_event = {
            'name': 'Transfer',
            'address': outcome_token_factory.address,
            'params': [
                {
                    'name': 'from',
                    'value': owner_one
                },
                {
                    'name': 'to',
                    'value': owner_two
                },
                {
                    'name': 'value',
                    'value': 10
                }
            ]
        }

        OutcomeTokenInstanceReceiver().save(issuance_event)
        OutcomeTokenInstanceReceiver().save(transfer_event)
        outcome_token_balance_before_rollback = OutcomeTokenBalance.objects.get(owner=owner_two)
        self.assertEquals(outcome_token_balance_before_rollback.balance, 10)

        # Rollback
        OutcomeTokenInstanceReceiver().rollback(transfer_event, block)
        with self.assertRaises(OutcomeTokenBalance.DoesNotExist):
            OutcomeTokenBalance.objects.get(owner=owner_two)

        # Test with funds on owner2
        OutcomeTokenInstanceReceiver().save(issuance_event)
        isuance_event_owner_two = issuance_event.copy()
        isuance_event_owner_two.get('params')[0]['value'] = owner_two
        OutcomeTokenInstanceReceiver().save(isuance_event_owner_two)
        OutcomeTokenInstanceReceiver().save(transfer_event)
        OutcomeTokenInstanceReceiver().rollback(transfer_event, block)
        owner_two_token_balance = OutcomeTokenBalance.objects.get(owner=owner_two)
        self.assertEquals(owner_two_token_balance.balance, 1000)