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
            'resolutionDate': datetime.now().isoformat(),
            'outcomes': ['YES', 'NO']
        }

        ipfs_hash = self.ipfs_api.post(event_description_json)

        block = {
            'number': oracle.creation_block,
            'timestamp': self.to_timestamp(oracle.creation_date_time)
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

        CentralizedOracleFactoryReceiver().save(oracle_event, block)
        created_oracle = CentralizedOracle.objects.get(address=oracle_address)
        self.assertIsNotNone(created_oracle.pk)

    def test_ultimate_oracle_receiver(self):
        forwarded_oracle = CentralizedOracleFactory()
        ultimate_oracle = UltimateOracleFactory()

        block = {
            'number': ultimate_oracle.creation_block,
            'timestamp': mktime(ultimate_oracle.creation_date_time.timetuple())
        }

        oracle_address = ultimate_oracle.address[0:7] + 'another'

        oracle_event = {
            'address': ultimate_oracle.factory[0:7] + 'another',
            'params': [
                {
                    'name': 'creator',
                    'value': ultimate_oracle.creator
                },
                {
                    'name': 'ultimateOracle',
                    'value': oracle_address,
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

        UltimateOracleFactoryReceiver().save(oracle_event, block)
        created_oracle = UltimateOracle.objects.get(address=oracle_address)
        self.assertIsNotNone(created_oracle.pk)

    def test_scalar_event_receiver(self):
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

    def test_categorical_event_receiver(self):
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

    def test_market_receiver(self):
        oracle = CentralizedOracleFactory()
        oracle.event_description.outcomes = ['1', '2', '3']
        oracle.event_description.save()
        event = CategoricalEventFactory(oracle=oracle)
        market = MarketFactory()
        event_address = event.address

        block = {
            'number': oracle.creation_block,
            'timestamp': self.to_timestamp(oracle.creation_date_time)
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
                },
                {
                    'name': 'market',
                    'value': market.address[0:7] + 'another'
                }
            ]
        }

        MarketFactoryReceiver().save(market_dict, block)
        with self.assertRaises(Market.DoesNotExist):
            Market.objects.get(event=event_address)


        market_dict.get('params')[2].update({'value': settings.LMSR_MARKET_MAKER})
        MarketFactoryReceiver().save(market_dict, block)
        market = Market.objects.get(event=event_address)
        self.assertIsNotNone(market.pk)
        self.assertEquals(len(market.net_outcome_tokens_sold), 3)

    #
    # contract instances
    #
    def test_event_instance_receiver(self):
        outcome_token_factory = OutcomeTokenFactory()
        oracle_factory = OracleFactory()
        event_factory = EventFactory()
        event_address = event_factory.address[0:-7] + 'GIACOMO'

        block = {
            'number': oracle_factory.creation_block,
            'timestamp': mktime(oracle_factory.creation_date_time.timetuple())
        }

        scalar_event = {
            'name': 'ScalarEventCreation',
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
                    'value': event_address
                }
            ]
        }

        EventFactoryReceiver().save(scalar_event, block)
        event = ScalarEvent.objects.get(address=event_address)

        block = {
            'number': oracle_factory.creation_block,
            'timestamp': mktime(oracle_factory.creation_date_time.timetuple())
        }
        outcome_token_address = oracle_factory.address[1:-8] + 'INSTANCE'
        outcome_event = {
            'name': 'OutcomeTokenCreation',
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
                    'value': outcome_token_address,
                },
                {
                    'name': 'index',
                    'value': outcome_token_factory.index
                }
            ]
        }
        EventInstanceReceiver().save(outcome_event, block)
        self.assertIsNotNone(OutcomeToken.objects.get(address=outcome_token_address))

    def test_event_instance_issuance_receiver(self):
        outcome_token_factory = OutcomeTokenFactory()
        event = {
            'name': 'Issuance',
            'address': outcome_token_factory.address,
            'params': [
                {
                    'name': 'owner',
                    'value': outcome_token_factory.address[0:-7] + 'GIACOMO'
                },
                {
                    'name': 'amount',
                    'value': 1000,
                }
            ]
        }

        OutcomeTokenInstanceReceiver().save(event)
        outcome_token = OutcomeToken.objects.get(address= outcome_token_factory.address)
        self.assertIsNotNone(outcome_token.pk)
        self.assertEquals(outcome_token_factory.total_supply + 1000, outcome_token.total_supply)

    def test_event_instance_revocation_receiver(self):
        outcome_token_factory = OutcomeTokenFactory()
        revocation_event = {
            'name': 'Revocation',
            'address': outcome_token_factory.address,
            'params': [
                {
                    'name': 'owner',
                    'value': outcome_token_factory.address[0:-7] + 'GIACOMO'
                },
                {
                    'name': 'amount',
                    'value': 1000,
                }
            ]
        }

        issuance_event = revocation_event.copy()
        issuance_event.update({'name': 'Issuance'})

        # do issuance
        OutcomeTokenInstanceReceiver().save(issuance_event)
        # do revocation
        OutcomeTokenInstanceReceiver().save(revocation_event)
        outcome_token = OutcomeToken.objects.get(address= outcome_token_factory.address)
        self.assertIsNotNone(outcome_token.pk)
        self.assertEquals(outcome_token_factory.total_supply, outcome_token.total_supply)

    def test_event_instance_outcome_assignment_receiver(self):
        event_factory = EventFactory()
        assignment_event = {
            'name': 'OutcomeAssignment',
            'address': event_factory.address,
            'params': [{
                'name': 'outcome',
                'value': 1,
            }]
        }

        EventInstanceReceiver().save(assignment_event)
        event = Event.objects.get(address=event_factory.address)
        self.assertTrue(event.is_winning_outcome_set)

    def test_event_instance_winnings_redemption_receiver(self):
        event_factory = EventFactory()
        redemption_event = {
            'name': 'WinningsRedemption',
            'address': event_factory.address,
            'params': [
                {
                    'name': 'receiver',
                    'value': event_factory.creator[0:-7] + 'GIACOMO',
                },
                {
                    'name': 'winnings',
                    'value': 1
                }
            ]
        }

        EventInstanceReceiver().save(redemption_event)
        event = Event.objects.get(address=event_factory.address)
        self.assertEquals(event.redeemed_winnings, event_factory.redeemed_winnings+1)

    def test_centralized_oracle_instance_owner_replacement_receiver(self):
        oracle_factory = CentralizedOracleFactory()
        new_owner = oracle_factory.address[0:-7] + 'GIACOMO'
        change_owner_event = {
            'name': 'OwnerReplacement',
            'address': oracle_factory.address,
            'params': [
                {
                    'name': 'newOwner',
                    'value': new_owner
                }
            ]
        }

        CentralizedOracleInstanceReceiver().save(change_owner_event)
        centralized_oracle = CentralizedOracle.objects.get(address=oracle_factory.address)
        self.assertEquals(centralized_oracle.owner, new_owner)

    def test_centralized_oracle_instance_outcome_assignment_receiver(self):
        oracle_factory = CentralizedOracleFactory()
        assignment_event = {
            'name': 'OutcomeAssignment',
            'address': oracle_factory.address,
            'params': [{
                'name': 'outcome',
                'value': 1,
            }]
        }

        CentralizedOracleInstanceReceiver().save(assignment_event)
        centralized_oracle = CentralizedOracle.objects.get(address=oracle_factory.address)
        self.assertTrue(centralized_oracle.is_outcome_set)
        self.assertEqual(centralized_oracle.outcome, 1)

    def test_ultimate_oracle_instance_outcome_assignment_receiver(self):
        oracle_factory = UltimateOracleFactory()
        assignment_event = {
            'name': 'ForwardedOracleOutcomeAssignment',
            'address': oracle_factory.address,
            'params': [{
                'name': 'outcome',
                'value': 1,
            }]
        }

        UltimateOracleInstanceReceiver().save(assignment_event)
        ultimate_oracle = UltimateOracle.objects.get(address=oracle_factory.address)
        self.assertTrue(ultimate_oracle.is_outcome_set)
        self.assertEqual(ultimate_oracle.forwarded_outcome, 1)

    def test_ultimate_oracle_instance_outcome_challenge_receiver(self):
        oracle = UltimateOracleFactory()
        assignment_event = {
            'name': 'OutcomeChallenge',
            'address': oracle.address,
            'params': [
                {
                    'name': 'sender',
                    'value': oracle.creator
                },
                {
                    'name': 'outcome',
                    'value': 1
                }
            ]
        }

        UltimateOracleInstanceReceiver().save(assignment_event)
        ultimate_oracle = UltimateOracle.objects.get(address=oracle.address)
        self.assertEqual(ultimate_oracle.total_amount, oracle.challenge_amount)
        self.assertEqual(ultimate_oracle.front_runner, 1)

    def test_ultimate_oracle_instance_outcome_vote_receiver(self):
        balance_factory = OutcomeVoteBalanceFactory()
        assignment_event = {
            'name': 'OutcomeVote',
            'address': balance_factory.ultimate_oracle.address,
            'params': [
                {
                    'name': 'outcome',
                    'value': balance_factory.ultimate_oracle.front_runner+1,
                },
                {
                    'name': 'amount',
                    'value': 1,
                },
                {
                    'name': 'sender',
                    'value': balance_factory.address,
                },
            ]
        }

        UltimateOracleInstanceReceiver().save(assignment_event)
        ultimate_oracle = UltimateOracle.objects.get(address=balance_factory.ultimate_oracle.address)
        outcome_vote_balance = OutcomeVoteBalance.objects.get(address= balance_factory.address)
        self.assertEquals(ultimate_oracle.total_amount, balance_factory.ultimate_oracle.total_amount+1)
        self.assertEquals(ultimate_oracle.front_runner, balance_factory.ultimate_oracle.front_runner+1)
        self.assertEquals(outcome_vote_balance.balance, 1)

    def test_ultimate_oracle_instance_withdrawal_receiver(self):
        balance_factory = OutcomeVoteBalanceFactory()
        assignment_event = {
            'name': 'Withdrawal',
            'address': balance_factory.ultimate_oracle.address,
            'params': [
                {
                    'name': 'amount',
                    'value': 1,
                },
                {
                    'name': 'sender',
                    'value': balance_factory.address,
                },
            ]
        }

        UltimateOracleInstanceReceiver().save(assignment_event)
        outcome_vote_balance = OutcomeVoteBalance.objects.get(address= balance_factory.address)
        self.assertEquals(outcome_vote_balance.balance, balance_factory.balance-1)

    def test_market_funding_receiver(self):
        market_factory = MarketFactory()
        funding_event = {
            'name': 'MarketFunding',
            'address': market_factory.address,
            'params': [
                {
                    'name': 'funding',
                    'value': 100
                }
            ]
        }

        MarketInstanceReceiver().save(funding_event)
        market = Market.objects.get(address=market_factory.address)
        self.assertEquals(market.stage, 1)
        self.assertEquals(market.funding, 100)

    def test_market_closing_receiver(self):
        market_factory = MarketFactory()
        closing_event = {
            'name': 'MarketClosing',
            'address': market_factory.address,
            'params': []
        }

        MarketInstanceReceiver().save(closing_event)
        market = Market.objects.get(address=market_factory.address)
        self.assertEquals(market.stage, 2)

    def test_market_fee_withdrawal_receiver(self):
        market_factory = MarketFactory()
        withdraw_event = {
            'name': 'FeeWithdrawal',
            'address': market_factory.address,
            'params': [
                {
                    'name': 'fees',
                    'value': 10
                }
            ]
        }

        MarketInstanceReceiver().save(withdraw_event)
        market = Market.objects.get(address=market_factory.address)
        # self.assertEquals(market.stage, 3)
        self.assertEquals(market.withdrawn_fees, market_factory.withdrawn_fees+10)

    def test_outcome_token_purchase(self):
        categorical_event = CategoricalEventFactory()
        outcome_token = OutcomeTokenFactory(event=categorical_event, index=0)
        market = MarketFactory(event=categorical_event)
        sender_address = '{:040d}'.format(100)

        outcome_token_purchase_event = {
            'name': 'OutcomeTokenPurchase',
            'address': market.address,
            'params': [
                {'name': 'outcomeTokenCost', 'value': 100},
                {'name': 'marketFees', 'value': 10},
                {'name': 'buyer', 'value': sender_address},
                {'name': 'outcomeTokenIndex', 'value': 0},
                {'name': 'outcomeTokenCount', 'value': 10},
            ]
        }

        block = {
            'number': 1,
            'timestamp': self.to_timestamp(datetime.now())
        }

        self.assertEquals(BuyOrder.objects.all().count(), 0)
        MarketInstanceReceiver().save(outcome_token_purchase_event, block)
        buy_orders = BuyOrder.objects.all()
        self.assertEquals(buy_orders.count(), 1)
        self.assertEquals(buy_orders[0].cost, 110) # outcomeTokenCost+fee

    def test_outcome_token_sell(self):
        categorical_event = CategoricalEventFactory()
        outcome_token = OutcomeTokenFactory(event=categorical_event, index=0)
        market = MarketFactory(event=categorical_event)
        sender_address = '{:040d}'.format(100)

        outcome_token_sell_event = {
            'name': 'OutcomeTokenSale',
            'address': market.address,
            'params': [
                {'name': 'outcomeTokenProfit', 'value': 100},
                {'name': 'marketFees', 'value': 10},
                {'name': 'seller', 'value': sender_address},
                {'name': 'outcomeTokenIndex', 'value': 0},
                {'name': 'outcomeTokenCount', 'value': 10},
            ]
        }

        block = {
            'number': 1,
            'timestamp': self.to_timestamp(datetime.now())
        }

        self.assertEquals(SellOrder.objects.all().count(), 0)
        MarketInstanceReceiver().save(outcome_token_sell_event, block)
        sell_orders = SellOrder.objects.all()
        self.assertEquals(sell_orders.count(), 1)
        self.assertEquals(sell_orders[0].profit, 90) # outcomeTokenProfit-fee

    def test_collected_fees(self):
        categorical_event = CategoricalEventFactory()
        outcome_token = OutcomeTokenFactory(event=categorical_event, index=0)
        market = MarketFactory(event=categorical_event)
        sender_address = '{:040d}'.format(100)
        fees = 10

        outcome_token_purchase_event = {
            'name': 'OutcomeTokenPurchase',
            'address': market.address,
            'params': [
                {'name': 'outcomeTokenCost', 'value': 100},
                {'name': 'marketFees', 'value': fees},
                {'name': 'buyer', 'value': sender_address},
                {'name': 'outcomeTokenIndex', 'value': 0},
                {'name': 'outcomeTokenCount', 'value': 10},
            ]
        }

        block = {
            'number': 1,
            'timestamp': self.to_timestamp(datetime.now())
        }

        # Save event
        MarketInstanceReceiver().save(outcome_token_purchase_event, block)
        # Check that collected fees was incremented
        market_check = Market.objects.get(address=market.address)
        self.assertEquals(market_check.collected_fees, market.collected_fees+fees)

        block.update({'number': 2})
        MarketInstanceReceiver().save(outcome_token_purchase_event, block)
        market_check = Market.objects.get(address=market.address)
        self.assertEquals(market_check.collected_fees, market.collected_fees+fees+fees)