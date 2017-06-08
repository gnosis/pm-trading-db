# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import factory
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


class ContractFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Contract

    address = factory.Sequence(lambda n: '{:020d}'.format(n))
    factory_address = factory.Sequence(lambda n: '{:020d}'.format(n))
    creator = factory.Sequence(lambda n: '{:020d}'.format(n))
    creation_date = FuzzyDateTime(datetime.now(pytz.utc))
    creation_block = factory.Sequence(lambda n: n)


class CollateralTokenFactory(ContractFactory):

    class Meta:
        model = models.CollateralToken


class OracleFactory(ContractFactory):

    class Meta:
        model = models.Oracle

    is_outcome_set = False
    outcome = factory.Sequence(lambda n: n)


class OutcomeTokenFactory(ContractFactory):

    class Meta:
        model = models.OutcomeToken


class EventFactory(ContractFactory):

    class Meta:
        model = models.Event

    collateral_token = factory.SubFactory(CollateralTokenFactory)
    oracle = factory.SubFactory(OracleFactory)
    is_winning_outcome_set = False
    winning_outcome = 1

    @factory.post_generation
    def outcome_tokens(self, create, extracted, **kwargs):
        """Manages many x many relationship"""
        if not create:
            return

        if extracted:
            for outcometoken in extracted:
                self.outcome_tokens.add(outcometoken)


class EventDescriptionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.EventDescription

    title = factory.Sequence(lambda _: faker.words(5))
    description = factory.Sequence(lambda _: faker.words(5))
    resolution_date = FuzzyDateTime(datetime.now(pytz.utc))


class CategoricalEventFactory(EventDescriptionFactory):
    class Meta:
        model = models.CategoricalEventDescription

    outcomes = [factory.Sequence(lambda _: faker.words(2)), factory.Sequence(lambda _: faker.words(2))]


class CentralizedOracleFactory(OracleFactory):

    class Meta:
        model = models.CentralizedOracle

    owner = factory.Sequence(lambda n: '{:020d}'.format(n))
    ipfs_hash = factory.Sequence(lambda n: '{:040d}'.format(n))
    event_description = factory.SubFactory(CategoricalEventFactory)


class UltimateOracleFactory(OracleFactory):

    class Meta:
        model = models.UltimateOracle

    forwarded_oracle = factory.SubFactory(OracleFactory)
    collateral_token = factory.SubFactory(CollateralTokenFactory)
    spread_multiplier = factory.Sequence(lambda n: n)
    challenge_period = factory.Sequence(lambda n: n)
    challenge_amount = factory.Sequence(lambda n: n)
    front_runner_period = factory.Sequence(lambda n: n)
    forwarded_outcome = factory.Sequence(lambda n: n)
    outcome_set_at_timestamp = factory.Sequence(lambda n: n)
    front_runner = factory.Sequence(lambda n: n)
    front_runner_set_at_timestamp = factory.Sequence(lambda n: n)
    total_amount = factory.Sequence(lambda n: n)


class MarketFactory(ContractFactory):

    class Meta:
        model = models.Market

    event = factory.SubFactory(EventFactory)
    market_maker = faker.name()
    fee = factory.Sequence(lambda n: n)
    funding = factory.Sequence(lambda n: n)
    net_outcome_tokens_sold = factory.Sequence(lambda n: n)
    outcome_probabilities = factory.Sequence(lambda n: n)

