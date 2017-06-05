import factory
from faker import Factory as FakerFactory
from factory.fuzzy import FuzzyDateTime
from . import models
import random
import hashlib
from datetime import datetime

faker = FakerFactory.create()

def randomSHA256():
    return hashlib.sha256(str(random.random())).hexdigest()


class ContractFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Contract

    address = factory.Sequence(lambda n: '0x{:040d}'.format(n))
    factory_address = factory.Sequence(lambda n: '0x{:040d}'.format(n))
    creator = factory.Sequence(lambda n: '0x{:040d}'.format(n))
    creation_date = factory.Sequence(lambda n: FuzzyDateTime(datetime(1, 1, 2016)))
    creation_block = factory.Sequence(lambda n: n)


class OracleFactory(ContractFactory):

    class Meta:
        model = models.Oracle

    is_outcome_set = False
    outcome = factory.Sequence(lambda n: n)


class CentralizedOracleFactory(OracleFactory):

    class Meta:
        model = models.CentralizedOracle

    owner = factory.Sequence(lambda n: '0x{:040d}'.format(n))
    ipfs_hash = factory.Sequence(lambda n: '0x{:040d}'.format(n))
    event_description = "event description"
