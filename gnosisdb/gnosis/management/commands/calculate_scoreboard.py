from cProfile import Profile
from datetime import timedelta
from decimal import Decimal
from operator import itemgetter

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count, F
from django.utils import timezone

from django_eth_events.utils import normalize_address_without_0x
from gnosisdb.relationaldb.models import (Event, Market, Order,
                                          OutcomeTokenBalance,
                                          TournamentParticipant,
                                          TournamentWhitelistedCreator)

OUTCOME_RANGE = 1000000


class Command(BaseCommand):
    help = 'Calculates the scoreboard for the tournament participants'

    def add_arguments(self, parser):
        parser.add_argument(
            '--profile',
            action='store_true',
            dest='profile',
            help='Show cProfile information',
        )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(args, kwargs)
        # Remove comment to enable reset:
        # self.reset()

    def reset(self):
        """Resets users data"""
        TournamentParticipant.objects.update(
            predictions=0,
            predicted_profit=0,
            score=0
        )
        self.stdout.write(self.style.SUCCESS('Reset TournamentParticipant data'))

    def store_scoreboard(self, users_predicted_values):
        """Updates the all the users values and calculates the scoreboard (rankings)"""
        self.stdout.write(self.style.SUCCESS('Starting updating users values {}'.format(timezone.now().strftime("%Y-%m-%d %H:%M:%S"))))
        with transaction.atomic():
            for index, user_predicted_value in enumerate(users_predicted_values):
                try:
                    TournamentParticipant.objects.filter(address=user_predicted_value['address']).update(
                        past_rank=F('current_rank'),
                        predicted_profit=user_predicted_value['predicted_profit'],
                        predictions=user_predicted_value['predictions'],
                        score=user_predicted_value['score'],
                        current_rank=index + 1,
                        diff_rank=F('past_rank') - F('current_rank'),
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR('Scoreboard Error: Was not possible updating user {} due to: {}'.format(user_predicted_value['address'],
                                                                                                                               e)))
        self.stdout.write(self.style.SUCCESS('Users updated successfully'))

    @staticmethod
    def calculate_scalar_event_value(event, outcome_token_balance):
        lower_bound = event.scalarevent.lower_bound
        upper_bound = event.scalarevent.upper_bound
        if event.outcome < 0:
            converted_winning_outcome = 0
        elif event.outcome > upper_bound:
            converted_winning_outcome = OUTCOME_RANGE
        else:
            converted_winning_outcome = OUTCOME_RANGE * (event.outcome - lower_bound) / (upper_bound - lower_bound)

        factor_short = OUTCOME_RANGE - converted_winning_outcome
        factor_long = OUTCOME_RANGE - factor_short

        outcome_token_index = outcome_token_balance.outcome_token.index
        if outcome_token_index == 0:
            return outcome_token_balance.balance * factor_short / OUTCOME_RANGE
        elif outcome_token_index == 1:
            return outcome_token_balance.balance * factor_long / OUTCOME_RANGE
        else:
            return 0

    def handle(self, *args, **options):
        """Command entrypoint"""

        if options['profile']:
            profiler = Profile()
            profiler.runcall(self._handle, *args, **options)
            profiler.print_stats()
        else:
            self._handle(*args, **options)

    def _handle(self, *args, **options):
        start_time = timezone.now()
        self.stdout.write(self.style.SUCCESS('Starting Scoreboard process, {}'.format(start_time.strftime("%Y-%m-%d %H:%M:%S"))))

        try:
            # Get the whitelisted markets creators
            whitelisted_creators = TournamentWhitelistedCreator.objects.filter(enabled=True).values_list('address',
                                                                                                         flat=True)
            # Get the whitelisted event addresses
            event_addresses = Event.objects.filter(creator__in=whitelisted_creators).values_list('address', flat=True)

            # Get the market addresses for the whitelisted events
            market_addresses = Market.objects.filter(event__in=event_addresses).values_list('address', flat=True)

            # Get users created until the last minute (to prevent reorgs)
            users = TournamentParticipant.objects.filter(
                created__lte=timezone.now() - timedelta(minutes=1)
            ).select_related('tournament_balance')

            users_addresses = users.values_list('address', flat=True)

            all_outcome_token_balances = OutcomeTokenBalance.objects.filter(
                owner__in=users_addresses,
                outcome_token__event__address__in=event_addresses,
                balance__gt=0
            ).select_related(
                'outcome_token__event__categoricalevent',
                'outcome_token__event__scalarevent',
            ).prefetch_related('outcome_token__event__markets')

            all_outcome_token_balances_dict = {}
            for outcome_token_balance in all_outcome_token_balances:
                all_outcome_token_balances_dict.setdefault(outcome_token_balance.owner, []).append(outcome_token_balance)

            all_orders = Order.objects.filter(
                sender__in=users_addresses,
                market__in=market_addresses,
            ).prefetch_related('market')

            # Participations of user in different markets
            distinct_participations = all_orders.values('sender').annotate(number_predictions=Count('market',
                                                                                                    distinct=True))
            # Get orders for every user, if there's more than one for a market just the latest one
            latest_orders = all_orders.distinct('market', 'sender').order_by('market', 'sender', '-creation_date_time')

            latest_orders_dict = {}
            for latest_order in latest_orders:
                latest_orders_dict.setdefault(latest_order.sender, []).append(latest_order)

            user_with_participations = {}
            for participation in distinct_participations:
                user_with_participations[participation['sender']] = participation['number_predictions']

            users_predicted_values = []
            for user in users:
                # Get balance
                user_address = normalize_address_without_0x(user.address.lower())
                balance = user.tournament_balance.balance

                # Number of markets the user is participating in
                predictions = user_with_participations.get(user_address, 0)

                user_outcome_token_balances = all_outcome_token_balances_dict.get(user_address, [])

                predicted_value = 0
                for outcome_token_balance in user_outcome_token_balances:
                    market = outcome_token_balance.outcome_token.event.markets.first()
                    event = outcome_token_balance.outcome_token.event
                    if event.is_winning_outcome_set:
                        outcome_token_index = outcome_token_balance.outcome_token.index
                        if event.is_categorical() and outcome_token_index == event.outcome:
                            predicted_value += outcome_token_balance.balance
                        elif event.is_scalar():
                            predicted_value += self.calculate_scalar_event_value(event, outcome_token_balance)

                    else:
                        try:
                            order = next(user_market_order for user_market_order in latest_orders_dict.get(user_address)
                                         if user_market_order.market_id == market.address)
                            outcome_token_index = order.outcome_token.index
                            marginal_price = order.marginal_prices[outcome_token_index]
                            predicted_value += (outcome_token_balance.balance * marginal_price)
                        except StopIteration:
                            # Bought all outcomes
                            if event.is_categorical():
                                marginal_price = Decimal(1 / event.outcome_tokens.count())
                            elif event.is_scalar():
                                marginal_price = Decimal(0.5)
                            else:
                                raise ValueError('Event is neither categorical nor scalar')
                            predicted_value += outcome_token_balance.balance * marginal_price

                users_predicted_values.append({
                    'balance': balance,
                    'predicted_profit': predicted_value,
                    'predictions': predictions,
                    'score': predicted_value + balance,
                    'address': user.address
                })

            sorted_scoreboard = sorted(users_predicted_values, key=itemgetter('score'), reverse=True)
            # Store scoreboard
            self.store_scoreboard(sorted_scoreboard)
        except Exception as e:
            self.stdout.write(self.style.ERROR("Scoreboard Error: {}".format(e)))
            raise e
        finally:
            end_time = timezone.now()
            delta = end_time - start_time
            total_seconds = delta.total_seconds()
            benchmark = divmod(total_seconds, 60)
            self.stdout.write(self.style.SUCCESS('Scoreboard calculation took {} minutes and {} seconds'.format(benchmark[0],
                                                                                                                benchmark[1])))
