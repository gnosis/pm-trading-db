from django.contrib.postgres.fields import ArrayField
from django.db import models
from model_utils.models import TimeStampedModel

# ==================================
#       Abstract classes
# ==================================

# Ethereum addresses have 40 chars (without 0x)
ADDRESS_LENGTH = 40


class BlockTimeStamped(models.Model):
    """Model created in a specific Ethereum block"""
    creation_date_time = models.DateTimeField()
    creation_block = models.PositiveIntegerField()

    class Meta:
        abstract = True


class Contract(models.Model):
    """Represents the Ethereum smart contract instance"""
    address = models.CharField(max_length=ADDRESS_LENGTH, primary_key=True)

    class Meta:
        abstract = True


class ContractCreatedByFactory(Contract, BlockTimeStamped):
    """Represents the Ethereum smart contract instance created by a factory (proxy contract)"""
    factory = models.CharField(max_length=ADDRESS_LENGTH, db_index=True)  # factory contract creating the contract
    creator = models.CharField(max_length=ADDRESS_LENGTH, db_index=True)  # address that initializes the transaction

    class Meta:
        abstract = True


# ==================================
#       Concrete classes
# ==================================


class Oracle(ContractCreatedByFactory):
    """Parent class of the Oracle contract"""
    is_outcome_set = models.BooleanField(default=False)
    outcome = models.DecimalField(max_digits=80,
                                  decimal_places=0,
                                  blank=True,
                                  null=True)

    def __str__(self):
        if self.is_outcome_set:
            return "Outcome {}".format(self.outcome)
        else:
            return ""


# Events
class Event(ContractCreatedByFactory):
    """Parent class of the event's classes."""
    oracle = models.ForeignKey(Oracle,
                               related_name='event_oracle',
                               db_column='oracle_address',
                               on_delete=models.CASCADE)  # Reference to the Oracle contract
    collateral_token = models.CharField(max_length=ADDRESS_LENGTH, db_index=True)  # The ERC20 token address used in the event to exchange outcome token shares
    is_winning_outcome_set = models.BooleanField(default=False)
    outcome = models.DecimalField(max_digits=80, decimal_places=0, null=True)
    redeemed_winnings = models.DecimalField(max_digits=80, decimal_places=0, default=0)  # Amount (in collateral token) of redeemed winnings once the event gets resolved

    def __str__(self):
        base = "Event with collateral_token {}".format(self.collateral_token)
        if self.is_winning_outcome_set:
            return "{} and outcome {}".format(base, self.outcome)
        else:
            return base

    def is_categorical(self):
        return hasattr(self, 'categoricalevent')

    def is_scalar(self):
        return hasattr(self, 'scalarevent')


class ScalarEvent(Event):
    """Events with continuous domain of possible outcomes
    between two boundaries: lower and upper bound"""
    lower_bound = models.DecimalField(max_digits=80, decimal_places=0)
    upper_bound = models.DecimalField(max_digits=80, decimal_places=0)

    def __str__(self):
        return "Lower bound {} and Upper bound {}".format(self.lower_bound,
                                                          self.upper_bound)


class CategoricalEvent(Event):
    """Events with discrete domain of possible outcomes"""
    pass


# Tokens
class OutcomeToken(Contract):
    """Representation of the ERC20 token related with its respective outcome in the event.
    This token is created by the Event smart contract letting the event to control supply."""
    event = models.ForeignKey(Event,
                              related_name='outcome_tokens',
                              db_column='event_address',
                              on_delete=models.CASCADE)  # The outcome token related event
    # index:
    # outcome position in the event's outcomes array (Categorical Event)
    # 0 for short and 1 for long position(Scalar Event)
    index = models.PositiveIntegerField()
    # total_supply: total amount of outcome tokens generated by the event for that outcome
    total_supply = models.DecimalField(max_digits=80,
                                       decimal_places=0,
                                       default=0)

    def __str__(self):
        return 'Index {} with total_supply {}'.format(self.index,
                                                      self.total_supply)


class OutcomeTokenBalance(models.Model):
    """Outcome token balance owned by an ethereum address owner"""
    owner = models.CharField(max_length=ADDRESS_LENGTH)
    outcome_token = models.ForeignKey(OutcomeToken,
                                      db_column='outcome_token_address',
                                      on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=80, decimal_places=0, default=0)

    def __str__(self):
        return 'Owner {} with balance {}'.format(self.owner,
                                                 self.balance)


# Event Descriptions
class EventDescription(models.Model):
    """Meta information of the event taken from IPFS"""
    title = models.TextField()
    description = models.TextField()
    resolution_date = models.DateTimeField()
    ipfs_hash = models.CharField(max_length=46, unique=True)

    def __str__(self):
        return '{} - {} - {}'.format(self.resolution_date,
                                     self.title,
                                     self.description)


class ScalarEventDescription(EventDescription):
    """Description for the Scalar Event"""
    unit = models.TextField()  # Example. USD, EUR, ETH
    decimals = models.PositiveIntegerField()  # the unit precision

    def __str__(self):
        base = super().__str__()
        return '{} - {}'.format(base, self.unit)


class CategoricalEventDescription(EventDescription):
    """Description for the Categorical Event"""
    outcomes = ArrayField(models.TextField())  # List of outcomes

    def __str__(self):
        base = super().__str__()
        return '{} - {}'.format(base, self.outcomes)


# Oracles
class CentralizedOracle(Oracle):
    """Centralized oracle model"""
    owner = models.CharField(max_length=ADDRESS_LENGTH, db_index=True)  # owner can be updated
    old_owner = models.CharField(max_length=ADDRESS_LENGTH, default=None, null=True)  # useful for rollback
    event_description = models.ForeignKey(EventDescription,
                                          unique=False,
                                          null=True,
                                          on_delete=models.CASCADE)

    def __str__(self):
        base = super().__str__()
        return 'Owner {} {}'.format(self.owner, base).strip()


# Market
class Market(ContractCreatedByFactory):
    """Market created by a the Gnosis standard market factory"""
    stages = (
        (0, 'MarketCreated'),
        (1, 'MarketFunded'),
        (2, 'MarketClosed'),
    )

    stages_dict = dict(stages)

    event = models.ForeignKey(Event,
                              related_name='markets',
                              db_column='event_address',
                              on_delete=models.CASCADE)
    market_maker = models.CharField(max_length=ADDRESS_LENGTH, db_index=True)  # the address of the market maker
    fee = models.PositiveIntegerField()
    funding = models.DecimalField(max_digits=80, decimal_places=0, null=True)
    net_outcome_tokens_sold = ArrayField(models.DecimalField(max_digits=80,
                                                             decimal_places=0),
                                         null=False)  # accumulative distribution of sold outcome tokens
    withdrawn_fees = models.DecimalField(max_digits=80, decimal_places=0, default=0)
    stage = models.PositiveIntegerField(choices=stages, default=0)
    revenue = models.DecimalField(max_digits=80, decimal_places=0)
    collected_fees = models.DecimalField(max_digits=80, decimal_places=0)
    marginal_prices = ArrayField(models.DecimalField(max_digits=5, decimal_places=4))
    trading_volume = models.DecimalField(max_digits=80, decimal_places=0)

    def __str__(self):
        return 'Market {} - {}'.format(self.address,
                                       self.stages_dict.get(self.stage, 'INVALID STAGE'))


class Order(BlockTimeStamped):
    """Parent class defining a market related order"""
    market = models.ForeignKey(Market,
                               related_name='orders',
                               db_column='market_address',
                               on_delete=models.CASCADE)
    sender = models.CharField(max_length=ADDRESS_LENGTH, db_index=True)
    outcome_token = models.ForeignKey(OutcomeToken,
                                      to_field='address',
                                      db_column='outcome_token_address',
                                      null=True,
                                      on_delete=models.CASCADE)
    outcome_token_count = models.DecimalField(max_digits=80, decimal_places=0)  # the amount of outcome tokens bought or sold
    net_outcome_tokens_sold = ArrayField(models.DecimalField(max_digits=80, decimal_places=0))  # represents the outcome tokens distrubition at the buy/sell order moment
    marginal_prices = ArrayField(models.DecimalField(max_digits=5, decimal_places=4))  # represent the marginal price of each outcome at the time of the market order

    def __str__(self):
        return 'Sender {} - Market {}'.format(self.sender, self.market_id)


class BuyOrder(Order):
    cost = models.DecimalField(max_digits=80, decimal_places=0)
    outcome_token_cost = models.DecimalField(max_digits=80, decimal_places=0)
    fees = models.DecimalField(max_digits=80, decimal_places=0)

    def __str__(self):
        base = super().__str__()
        return '{} - Cost {} - Outcome Token Cost {}'.format(base,
                                                             self.cost,
                                                             self.outcome_token_cost)


class SellOrder(Order):
    profit = models.DecimalField(max_digits=80, decimal_places=0)
    outcome_token_profit = models.DecimalField(max_digits=80, decimal_places=0)
    fees = models.DecimalField(max_digits=80, decimal_places=0)

    def __str__(self):
        base = super().__str__()
        return '{} - Profit {} - Outcome Token Profit {}'.format(base,
                                                                 self.profit,
                                                                 self.outcome_token_profit)


class ShortSellOrder(Order):
    cost = models.DecimalField(max_digits=80, decimal_places=0)

    def __str__(self):
        base = super().__str__()
        return '{} - Cost {}'.format(base, self.cost)


# ==================================
#      Tournament classes
# ==================================
class TournamentParticipant(Contract, TimeStampedModel, BlockTimeStamped):
    """Tournament participant"""
    current_rank = models.IntegerField()  # current rank position
    past_rank = models.IntegerField(default=0)  # previous rank position
    diff_rank = models.IntegerField(default=0)  # difference between current and previous rank position
    score = models.DecimalField(max_digits=80, decimal_places=0, default=0)  # sum of OLY balance and predicted profit
    predicted_profit = models.DecimalField(max_digits=80, decimal_places=0, default=0)  # outcome tokens current price
    predictions = models.IntegerField(default=0)  # number of events the user is participating in
    tokens_issued = models.BooleanField(default=False)  # True if the user already issued tokens
    mainnet_address = models.CharField(max_length=ADDRESS_LENGTH, default=None, null=True)


class TournamentParticipantBalance(models.Model):
    """Defines the participant's balance"""
    balance = models.DecimalField(max_digits=80, decimal_places=0, default=0)
    participant = models.OneToOneField(TournamentParticipant,
                                       to_field='address',
                                       db_column='participant_address',
                                       related_name='tournament_balance',
                                       on_delete=models.CASCADE)


class TournamentWhitelistedCreator(models.Model):
    address = models.CharField(max_length=ADDRESS_LENGTH, primary_key=True)
    enabled = models.BooleanField(default=True)