from __future__ import unicode_literals

from django.db import models
from django.core.validators import validate_comma_separated_integer_list
from django.contrib.postgres.fields import ArrayField


# Abstract Contract Structure
class Contract(models.Model):
    address = models.CharField(max_length=20, primary_key=True)
    # todo rename to factory
    factory_address = models.CharField(max_length=20)
    creator = models.CharField(max_length=20)
    creation_date = models.DateTimeField()
    creation_block = models.PositiveIntegerField()

    class Meta:
        abstract = True


# Tokens
class OutcomeToken(Contract):
    pass


class CollateralToken(Contract):
    pass


# Events
class Event(Contract):
    collateral_token = models.ForeignKey('CollateralToken')
    oracle = models.ForeignKey('Oracle')
    is_winning_outcome_set = models.BooleanField()
    winning_outcome = models.DecimalField(max_digits=80, decimal_places=0)
    outcome_tokens = models.ManyToManyField('OutcomeToken')


class ScalarEvent(Event):
    lower_bound = models.DecimalField(max_digits=80, decimal_places=0)
    upper_bound = models.DecimalField(max_digits=80, decimal_places=0)


class CategoricalEvent(Event):
    pass


# Event Descriptions
class EventDescription(models.Model):
    title = models.TextField()
    description = models.TextField()
    resolution_date = models.DateTimeField()


class ScalarEventDescription(EventDescription):
    unit = models.TextField()
    decimals = models.IntegerField()


class CategoricalEventDescription(EventDescription):
    outcomes = ArrayField(models.TextField())


# Oracles
class Oracle(Contract):
    is_outcome_set = models.BooleanField()
    outcome = models.DecimalField(max_digits=80, decimal_places=0)


class CentralizedOracle(Oracle):
    owner = models.CharField(max_length=20)
    ipfs_hash = models.TextField()
    event_description = models.ForeignKey('EventDescription')


class UltimateOracle(Oracle):
    forwarded_oracle = models.ForeignKey('Oracle', related_name='ultimate_oracle_forwarded_oracle')
    collateral_token = models.ForeignKey("CollateralToken")
    spread_multiplier = models.DecimalField(max_digits=80, decimal_places=0)
    challenge_period = models.DecimalField(max_digits=80, decimal_places=0)
    challenge_amount = models.DecimalField(max_digits=80, decimal_places=0)
    front_runner_period = models.DecimalField(max_digits=80, decimal_places=0)
    forwarded_outcome = models.DecimalField(max_digits=80, decimal_places=0)
    outcome_set_at_timestamp = models.DecimalField(max_digits=80, decimal_places=0)
    front_runner = models.DecimalField(max_digits=80, decimal_places=0)
    front_runner_set_at_timestamp = models.DecimalField(max_digits=80, decimal_places=0)
    total_amount = models.DecimalField(max_digits=80, decimal_places=0)


# Market
class Market(Contract):
    event = models.ForeignKey('Event')
    market_maker = models.CharField(max_length=20)
    fee = models.DecimalField(max_digits=80, decimal_places=0)
    funding = models.DecimalField(max_digits=80, decimal_places=0)
    net_outcome_tokens_sold = models.TextField(validators=[validate_comma_separated_integer_list])
    outcome_probabilities = models.TextField(validators=[validate_comma_separated_integer_list])
