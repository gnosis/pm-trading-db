from __future__ import unicode_literals

from django.db import models
from django.core.validators import validate_comma_separated_integer_list
from django.contrib.postgres.fields import ArrayField


# Abstract Contract Structure
class Contract(models.Model):
    address = models.CharField(max_length=40, primary_key=True)
    factory = models.CharField(max_length=40) # factory contract creating the contract
    creator = models.CharField(max_length=40)
    creation_date = models.DateTimeField()
    creation_block = models.PositiveIntegerField()

    class Meta:
        abstract = True


# Events
class Event(Contract):
    collateral_token = models.CharField(max_length=40)
    oracle = models.ForeignKey('Oracle')
    is_winning_outcome_set = models.BooleanField(default=False)
    winning_outcome = models.BigIntegerField(null=True)


class ScalarEvent(Event):
    lower_bound = models.BigIntegerField()
    upper_bound = models.BigIntegerField()


class CategoricalEvent(Event):
    pass


# Tokens
class OutcomeToken(Contract):
    event = models.ForeignKey(Event)


# Event Descriptions
class EventDescription(models.Model):
    title = models.TextField()
    description = models.TextField()
    resolution_date = models.DateTimeField()
    ipfs_hash = models.CharField(max_length=46, unique=True)

    # class Meta:
    #     abstract = True


class ScalarEventDescription(EventDescription):
    unit = models.TextField()
    decimals = models.PositiveIntegerField()


class CategoricalEventDescription(EventDescription):
    outcomes = ArrayField(models.TextField())


# Oracles
class Oracle(Contract):
    is_outcome_set = models.BooleanField(default=False)
    outcome = models.BigIntegerField(blank=True, null=True)


class CentralizedOracle(Oracle):
    owner = models.CharField(max_length=40) # owner can be updated
    event_description = models.ForeignKey('EventDescription', unique=False, null=True)


class UltimateOracle(Oracle):
    forwarded_oracle = models.ForeignKey('Oracle', related_name='ultimate_oracle_forwarded_oracle', null=True)
    collateral_token = models.CharField(max_length=40)
    spread_multiplier = models.PositiveIntegerField()
    challenge_period = models.BigIntegerField()
    challenge_amount = models.BigIntegerField()
    front_runner_period = models.BigIntegerField()
    forwarded_outcome = models.BigIntegerField(null=True)
    outcome_set_at_timestamp = models.BigIntegerField(null=True)
    front_runner = models.BigIntegerField(null=True)
    front_runner_set_at_timestamp = models.BigIntegerField(null=True)
    total_amount = models.BigIntegerField(null=True)


# Market
class Market(Contract):
    event = models.ForeignKey('Event')
    market_maker = models.CharField(max_length=40)
    fee = models.PositiveIntegerField()
    funding = models.BigIntegerField(null=True)
    net_outcome_tokens_sold = models.TextField(validators=[validate_comma_separated_integer_list], null=True)
    # outcome_probabilities = models.TextField(validators=[validate_comma_separated_integer_list])
    stage = models.PositiveIntegerField(null=True)
