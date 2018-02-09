# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import factory as factory_boy
from faker import Factory as FakerFactory, Faker
from factory.fuzzy import FuzzyDateTime
from relationaldb import models
import random
import hashlib
from datetime import datetime
import pytz

fakerFactory = FakerFactory.create()
faker = Faker()


def randomSHA256():
    return hashlib.sha256(str(random.random())).hexdigest()


class BlockTimestampedFactory(factory_boy.Factory):
    creation_date_time = FuzzyDateTime(datetime.now(pytz.utc))
    creation_block = factory_boy.Sequence(lambda n: n)


class ContractFactory(factory_boy.DjangoModelFactory):

    class Meta:
        model = models.Contract

    address = factory_boy.Sequence(lambda n: '{:040d}'.format(n))


class ContractCreatedByFactory(ContractFactory, BlockTimestampedFactory):

    class Meta:
        model = models.ContractCreatedByFactory

    factory = factory_boy.Sequence(lambda n: '{:040d}'.format(n))
    creator = factory_boy.Sequence(lambda n: '{:040d}'.format(n))

class EventDescriptionFactory(factory_boy.DjangoModelFactory):
    class Meta:
        model = models.EventDescription

    title = factory_boy.Sequence(lambda _: ' '.join(faker.words(5)))
    description = factory_boy.Sequence(lambda _: ' '.join(faker.words(5)))
    resolution_date = FuzzyDateTime(datetime.now(pytz.utc))
    ipfs_hash = factory_boy.Sequence(lambda n: '{:046d}'.format(n))


class CategoricalEventDescriptionFactory(EventDescriptionFactory):
    class Meta:
        model = models.CategoricalEventDescription

    outcomes = factory_boy.LazyAttribute(lambda _: [' '.join(faker.words(2)), ' '.join(faker.words(2))])


class ScalarEventDescriptionFactory(EventDescriptionFactory):
    class Meta:
        model = models.ScalarEventDescription

    unit = factory_boy.Sequence(lambda _: ' '.join(faker.words(1)))
    decimals = factory_boy.Sequence(lambda n: n)


class OracleFactory(ContractCreatedByFactory):

    class Meta:
        model = models.Oracle

    is_outcome_set = False
    outcome = factory_boy.Sequence(lambda n: n)


class CentralizedOracleFactory(OracleFactory):

    class Meta:
        model = models.CentralizedOracle

    owner = factory_boy.Sequence(lambda n: '{:040d}'.format(n))
    old_owner = None
    event_description = factory_boy.SubFactory(CategoricalEventDescriptionFactory)


class EventFactory(ContractCreatedByFactory):

    class Meta:
        model = models.Event

    collateral_token = factory_boy.Sequence(lambda n: '{:040d}'.format(n))
    oracle = factory_boy.SubFactory(CentralizedOracleFactory)
    is_winning_outcome_set = False
    outcome = 1
    redeemed_winnings = 0


class CategoricalEventFactory(EventFactory):
    class Meta:
        model = models.CategoricalEvent


class ScalarEventFactory(EventFactory):
    class Meta:
        model = models.ScalarEvent

    upper_bound = 1
    lower_bound = 0


class OutcomeTokenFactory(ContractFactory):

    class Meta:
        model = models.OutcomeToken

    event = factory_boy.SubFactory(CategoricalEventFactory)
    index = 1
    total_supply = factory_boy.Sequence(lambda n: n)


class OutcomeTokenBalanceFactory(factory_boy.DjangoModelFactory):

    class Meta:
        model = models.OutcomeTokenBalance

    outcome_token = factory_boy.SubFactory(OutcomeTokenFactory)
    balance = factory_boy.Sequence(lambda n: n)
    owner = factory_boy.Sequence(lambda n: '{:040d}'.format(n))


class MarketFactory(ContractCreatedByFactory):

    class Meta:
        model = models.Market

    event = factory_boy.SubFactory(CategoricalEventFactory)
    market_maker = factory_boy.Sequence(lambda n: '{:040d}'.format(n))
    fee = factory_boy.Sequence(lambda n: n)
    funding = factory_boy.Sequence(lambda n: (n+1)*1e18)
    net_outcome_tokens_sold = [0, 0]
    marginal_prices = ['0.5000', '0.5000']
    withdrawn_fees = 0
    trading_volume = 0
    # outcome_probabilities = factory.Sequence(lambda n: n)
    stage = 0
    revenue = factory_boy.Sequence(lambda n: n)
    collected_fees = 0


class OrderFactory(BlockTimestampedFactory, factory_boy.DjangoModelFactory):
    market = factory_boy.SubFactory(MarketFactory)
    sender = factory_boy.Sequence(lambda n: '{:040d}'.format(n))
    outcome_token = factory_boy.SubFactory(OutcomeTokenFactory)
    outcome_token_count = factory_boy.Sequence(lambda n: n)
    net_outcome_tokens_sold = [0, 0]
    marginal_prices = ['0.5000', '0.5000']


class BuyOrderFactory(OrderFactory):
    class Meta:
        model = models.BuyOrder

    cost = factory_boy.Sequence(lambda n: n)
    outcome_token_cost = factory_boy.Sequence(lambda n: n)
    fees = 0


class SellOrderFactory(OrderFactory):
    class Meta:
        model = models.SellOrder

    profit = factory_boy.Sequence(lambda n: n)
    outcome_token_profit = factory_boy.Sequence(lambda n: n)
    fees = 0


class TournamentParticipantFactory(ContractCreatedByFactory):
    class Meta:
        model = models.TournamentParticipant

    current_rank = factory_boy.Sequence(lambda n: n)
    past_rank = factory_boy.Sequence(lambda n: n)
    diff_rank = factory_boy.Sequence(lambda n: n)
    score = factory_boy.Sequence(lambda n: (n+1)*1e18)
    predicted_profit = factory_boy.Sequence(lambda n: n)
    predictions = factory_boy.Sequence(lambda n: n)


class TournamentParticipantBalanceFactory(factory_boy.DjangoModelFactory):

    class Meta:
        model = models.TournamentParticipantBalance

    balance = factory_boy.Sequence(lambda n: (n * 100))
    participant = factory_boy.SubFactory(TournamentParticipantFactory)