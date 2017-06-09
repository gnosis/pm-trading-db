# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import factory as factory_boy
from faker import Factory as FakerFactory, Faker
from factory.fuzzy import FuzzyDateTime
from gnosisdb.relationaldb import models
import random
import hashlib
from datetime import datetime
import pytz

fakerFactory = FakerFactory.create()
faker = Faker()


def randomSHA256():
    return hashlib.sha256(str(random.random())).hexdigest()


class ContractFactory(factory_boy.DjangoModelFactory):

    class Meta:
        model = models.Contract

    address = factory_boy.Sequence(lambda n: '{:020d}'.format(n))
    factory = factory_boy.Sequence(lambda n: '{:020d}'.format(n))
    creator = factory_boy.Sequence(lambda n: '{:020d}'.format(n))
    creation_date = FuzzyDateTime(datetime.now(pytz.utc))
    creation_block = factory_boy.Sequence(lambda n: n)


class OracleFactory(ContractFactory):

    class Meta:
        model = models.Oracle

    is_outcome_set = False
    outcome = factory_boy.Sequence(lambda n: n)


class EventFactory(ContractFactory):

    class Meta:
        model = models.Event

    collateral_token = factory_boy.Sequence(lambda n: '{:020d}'.format(n))
    oracle = factory_boy.SubFactory(OracleFactory)
    is_winning_outcome_set = False
    winning_outcome = 1


class OutcomeTokenFactory(ContractFactory):

    class Meta:
        model = models.OutcomeToken

    event = factory_boy.SubFactory(EventFactory)


class EventDescriptionFactory(factory_boy.DjangoModelFactory):
    class Meta:
        model = models.EventDescription

    title = factory_boy.Sequence(lambda _: faker.words(5))
    description = factory_boy.Sequence(lambda _: faker.words(5))
    resolution_date = FuzzyDateTime(datetime.now(pytz.utc))
    ipfs_hash = factory_boy.Sequence(lambda n: '{:046d}'.format(n))


class CategoricalEventFactory(EventDescriptionFactory):
    class Meta:
        model = models.CategoricalEventDescription

    outcomes = [factory_boy.Sequence(lambda _: faker.words(2)), factory_boy.Sequence(lambda _: faker.words(2))]


class CentralizedOracleFactory(OracleFactory):

    class Meta:
        model = models.CentralizedOracle

    owner = factory_boy.Sequence(lambda n: '{:020d}'.format(n))
    event_description = factory_boy.SubFactory(CategoricalEventFactory)


class UltimateOracleFactory(OracleFactory):

    class Meta:
        model = models.UltimateOracle

    forwarded_oracle = factory_boy.SubFactory(OracleFactory)
    collateral_token = factory_boy.Sequence(lambda n: '{:020d}'.format(n))
    spread_multiplier = factory_boy.Sequence(lambda n: n)
    challenge_period = factory_boy.Sequence(lambda n: n)
    challenge_amount = factory_boy.Sequence(lambda n: n)
    front_runner_period = factory_boy.Sequence(lambda n: n)
    forwarded_outcome = factory_boy.Sequence(lambda n: n)
    outcome_set_at_timestamp = factory_boy.Sequence(lambda n: n)
    front_runner = factory_boy.Sequence(lambda n: n)
    front_runner_set_at_timestamp = factory_boy.Sequence(lambda n: n)
    total_amount = factory_boy.Sequence(lambda n: n)


class MarketFactory(ContractFactory):

    class Meta:
        model = models.Market

    event = factory_boy.SubFactory(EventFactory)
    market_maker = faker.name()
    fee = factory_boy.Sequence(lambda n: n)
    funding = factory_boy.Sequence(lambda n: n)
    net_outcome_tokens_sold = factory_boy.Sequence(lambda n: n)
    # outcome_probabilities = factory.Sequence(lambda n: n)
    stage = factory_boy.Sequence(lambda n: n)

