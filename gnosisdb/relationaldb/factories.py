# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import factory
from faker import Factory as FakerFactory
from factory.fuzzy import FuzzyDateTime
from relationaldb import models
import random
import hashlib
from datetime import datetime
import pytz

faker = FakerFactory.create()


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


class OracleFactory(ContractFactory):

    class Meta:
        model = models.Oracle

    is_outcome_set = False
    outcome = factory.Sequence(lambda n: n)


class CentralizedOracleFactory(OracleFactory):

    class Meta:
        model = models.CentralizedOracle

    owner = factory.Sequence(lambda n: '{:020d}'.format(n))
    ipfs_hash = factory.Sequence(lambda n: '{:040d}'.format(n))
    event_description = "event description"
