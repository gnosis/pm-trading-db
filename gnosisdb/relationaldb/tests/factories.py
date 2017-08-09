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


class OracleFactory(ContractCreatedByFactory):

    class Meta:
        model = models.Oracle

    is_outcome_set = False
    outcome = factory_boy.Sequence(lambda n: n)


class EventFactory(ContractCreatedByFactory):

    class Meta:
        model = models.Event

    collateral_token = factory_boy.Sequence(lambda n: '{:040d}'.format(n))
    oracle = factory_boy.SubFactory(OracleFactory)
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

    event = factory_boy.SubFactory(EventFactory)
    index = 1
    total_supply = factory_boy.Sequence(lambda n: n)


class OutcomeTokenBalanceFactory(factory_boy.DjangoModelFactory):

    class Meta:
        model = models.OutcomeTokenBalance

    outcome_token = factory_boy.SubFactory(OutcomeTokenFactory)
    balance = factory_boy.Sequence(lambda n: n)
    owner = factory_boy.Sequence(lambda n: '{:040d}'.format(n))


class EventDescriptionFactory(factory_boy.DjangoModelFactory):
    class Meta:
        model = models.EventDescription

    title = factory_boy.Sequence(lambda _: faker.words(5))
    description = factory_boy.Sequence(lambda _: faker.words(5))
    resolution_date = FuzzyDateTime(datetime.now(pytz.utc))
    ipfs_hash = factory_boy.Sequence(lambda n: '{:046d}'.format(n))


class CategoricalEventDescriptionFactory(EventDescriptionFactory):
    class Meta:
        model = models.CategoricalEventDescription

    outcomes = [factory_boy.Sequence(lambda _: faker.words(2)), factory_boy.Sequence(lambda _: faker.words(2))]


class ScalarEventDescriptionFactory(EventDescriptionFactory):
    class Meta:
        model = models.ScalarEventDescription

    unit = factory_boy.Sequence(lambda _: faker.words(1))
    decimals = factory_boy.Sequence(lambda n: n)


class CentralizedOracleFactory(OracleFactory):

    class Meta:
        model = models.CentralizedOracle

    owner = factory_boy.Sequence(lambda n: '{:040d}'.format(n))
    event_description = factory_boy.SubFactory(CategoricalEventDescriptionFactory)


class UltimateOracleFactory(OracleFactory):

    class Meta:
        model = models.UltimateOracle

    forwarded_oracle = factory_boy.SubFactory(OracleFactory)
    collateral_token = factory_boy.Sequence(lambda n: '{:040d}'.format(n))
    spread_multiplier = factory_boy.Sequence(lambda n: n)
    challenge_period = factory_boy.Sequence(lambda n: n)
    challenge_amount = factory_boy.Sequence(lambda n: n)
    front_runner_period = factory_boy.Sequence(lambda n: n)
    forwarded_outcome = factory_boy.Sequence(lambda n: n)
    outcome_set_at_timestamp = factory_boy.Sequence(lambda n: n)
    front_runner = factory_boy.Sequence(lambda n: n)
    front_runner_set_at_timestamp = factory_boy.Sequence(lambda n: n)
    total_amount = factory_boy.Sequence(lambda n: n)


class OutcomeVoteBalanceFactory(factory_boy.DjangoModelFactory):

    class Meta:
        model = models.OutcomeVoteBalance

    ultimate_oracle = factory_boy.SubFactory(UltimateOracleFactory)
    address = factory_boy.Sequence(lambda n: '{:040d}'.format(n))
    balance = factory_boy.Sequence(lambda n: n)


class MarketFactory(ContractCreatedByFactory):

    class Meta:
        model = models.Market

    event = factory_boy.SubFactory(EventFactory)
    market_maker = factory_boy.Sequence(lambda n: '{:040d}'.format(n))
    fee = factory_boy.Sequence(lambda n: n)
    funding = factory_boy.Sequence(lambda n: n)
    net_outcome_tokens_sold = [0, 0]
    withdrawn_fees = 0
    # outcome_probabilities = factory.Sequence(lambda n: n)
    stage = 0
    revenue = factory_boy.Sequence(lambda n: n)
    collected_fees = 0
