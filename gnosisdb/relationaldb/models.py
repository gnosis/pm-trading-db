from __future__ import unicode_literals

from django.db import models
from django.core.validators import validate_comma_separated_integer_list


# Abstract Contract Structure
class Contract(models.Model):
    address = models.CharField(max_length=20, primary_key=True)
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
    winning_outcome = models.BigIntegerField()
    outcome_tokens = models.ManyToManyField('OutcomeToken')


class ScalarEvent(Event):
    lower_bound = models.BigIntegerField()
    upper_bound = models.BigIntegerField()


class CategoricalEvent(Event):
    pass


# Event Descriptions
class EventDescription(models.Model):
    title = models.TextField()
    description = models.TextField()
    resolution_date = models.DateTimeField()

    class Meta:
        abstract = True


class ScalarEventDescription(EventDescription):
    lower_bound = models.BigIntegerField()
    upper_bound = models.BigIntegerField()


class CategoricalEventDescription(EventDescription):
    pass


# Oracles
class Oracle(Contract):
    is_outcome_set = models.BooleanField()
    outcome = models.BigIntegerField()


class CentralizedOracle(Oracle):
    owner = models.CharField(max_length=20)
    ipfs_hash = models.TextField()
    event_description = models.TextField()


class UltimateOracle(Oracle):
    forwarded_oracle = models.ForeignKey('Oracle', related_name='ultimate_oracle_forwarded_oracle')
    collateral_token = models.ForeignKey("CollateralToken")
    spread_multiplier = models.BigIntegerField()
    challenge_period = models.BigIntegerField()
    challenge_amount = models.BigIntegerField()
    front_runner_period = models.BigIntegerField()
    forwarded_outcome = models.BigIntegerField()
    outcome_set_at_timestamp = models.BigIntegerField()
    front_runner = models.BigIntegerField()
    front_runner_set_at_timestamp = models.BigIntegerField()
    total_amount = models.BigIntegerField()


# Market
class Market(Contract):
    event = models.ForeignKey('Event')
    market_maker = models.CharField(max_length=20)
    fee = models.BigIntegerField()
    funding = models.BigIntegerField()
    net_outcome_tokens_sold = models.TextField(validators=[validate_comma_separated_integer_list])
    outcome_probabilities = models.TextField(validators=[validate_comma_separated_integer_list])
