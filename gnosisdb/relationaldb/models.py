from __future__ import unicode_literals

from django.db import models
from .validators import validate_numeric_dictionary
from django.contrib.postgres.fields import ArrayField
import json


class BlockTimeStamped(models.Model):
    creation_date_time = models.DateTimeField()
    creation_block = models.PositiveIntegerField()

    class Meta:
        abstract = True


# Abstract Contract Structure
class Contract(models.Model):
    address = models.CharField(max_length=40, primary_key=True)

    class Meta:
        abstract = True


class ContractCreatedByFactory(Contract, BlockTimeStamped):
    factory = models.CharField(max_length=40, db_index=True)  # factory contract creating the contract
    creator = models.CharField(max_length=40, db_index=True)

    class Meta:
        abstract = True


class Oracle(ContractCreatedByFactory):
    is_outcome_set = models.BooleanField(default=False)
    outcome = models.BigIntegerField(blank=True, null=True)


# Events
class Event(ContractCreatedByFactory):
    oracle = models.ForeignKey(Oracle, related_name='event_oracle')
    collateral_token = models.CharField(max_length=40, db_index=True)
    is_winning_outcome_set = models.BooleanField(default=False)
    outcome = models.BigIntegerField(null=True)
    redeemed_winnings = models.BigIntegerField(default=0)


class ScalarEvent(Event):
    lower_bound = models.BigIntegerField()
    upper_bound = models.BigIntegerField()


class CategoricalEvent(Event):
    pass


# Tokens
class OutcomeToken(Contract):
    event = models.ForeignKey(Event)
    index = models.PositiveIntegerField()
    total_supply = models.BigIntegerField(default=0)


class OutcomeTokenBalance(models.Model):
    owner = models.CharField(max_length=40)
    outcome_token = models.ForeignKey(OutcomeToken)
    balance = models.BigIntegerField(default=0)


# Event Descriptions
class EventDescription(models.Model):
    title = models.TextField()
    description = models.TextField()
    resolution_date = models.DateTimeField()
    ipfs_hash = models.CharField(max_length=46, unique=True)


class ScalarEventDescription(EventDescription):
    unit = models.TextField()
    decimals = models.PositiveIntegerField()


class CategoricalEventDescription(EventDescription):
    outcomes = ArrayField(models.TextField())


# Oracles
class CentralizedOracle(Oracle):
    owner = models.CharField(max_length=40, db_index=True) # owner can be updated
    event_description = models.ForeignKey(EventDescription, unique=False, null=True)


class UltimateOracle(Oracle):
    forwarded_oracle = models.ForeignKey(Oracle, related_name='ultimate_oracle_forwarded_oracle', null=True)
    collateral_token = models.CharField(max_length=40, db_index=True)
    spread_multiplier = models.PositiveIntegerField()
    challenge_period = models.BigIntegerField()
    challenge_amount = models.BigIntegerField()
    front_runner_period = models.BigIntegerField()
    forwarded_outcome = models.BigIntegerField(null=True)
    outcome_set_at_timestamp = models.BigIntegerField(null=True)
    front_runner = models.BigIntegerField(null=True)
    front_runner_set_at_timestamp = models.BigIntegerField(null=True)
    total_amount = models.BigIntegerField(null=True)


class OutcomeVoteBalance(models.Model):

    class Meta:
        unique_together = ('ultimate_oracle', 'address',)

    ultimate_oracle = models.ForeignKey(UltimateOracle, related_name='outcome_vote_balance_ultimate_oracle')
    address = models.CharField(max_length=40) # sender
    balance = models.BigIntegerField()


# Market
class Market(ContractCreatedByFactory):
    stages = (
        (0, 'MarketCreated'),
        (1, 'MarketFunded'),
        (2, 'MarketClosed'),
    )

    event = models.ForeignKey(Event, related_name='market_oracle')
    market_maker = models.CharField(max_length=40, db_index=True)
    fee = models.PositiveIntegerField()
    funding = models.BigIntegerField(null=True)
    # net_outcome_tokens_sold = models.TextField(validators=[validate_numeric_dictionary], null=True)
    net_outcome_tokens_sold = ArrayField(models.BigIntegerField(), null=False)
    withdrawn_fees = models.BigIntegerField(default=0)
    stage = models.PositiveIntegerField(choices=stages, default=0)
    revenue = models.BigIntegerField()
    collected_fees = models.BigIntegerField()


class Order(BlockTimeStamped):
    market = models.ForeignKey(Market)
    sender = models.CharField(max_length=40, db_index=True)
    outcome_token_index = models.PositiveIntegerField()
    outcome_token_count = models.BigIntegerField()
    net_outcome_tokens_sold = ArrayField(models.BigIntegerField()) # models.TextField(validators=[validate_numeric_dictionary], null=True)


class BuyOrder(Order):
    cost = models.BigIntegerField()


class SellOrder(Order):
    profit = models.BigIntegerField()


class ShortSellOrder(Order):
    cost = models.BigIntegerField()

