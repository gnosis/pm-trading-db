from django.core.management.base import BaseCommand
from relationaldb.models import (
    Event, TournamentWhitelistedCreator, TournamentParticipant, OutcomeTokenBalance, Order,
    TournamentParticipantBalance
)

from django.db import connections
from datetime import datetime, timedelta
from django.db import transaction
from operator import itemgetter

OUTCOME_RANGE = 1000000


class Command(BaseCommand):
    help = 'Calculates the scoreboard for the tournament participants'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(args, kwargs)
        # Remove comment to enable reset:
        # self.reset()

    def reset(self):
        """Resets users data"""
        cursor = None
        try:
            cursor = connections['default'].cursor()
            cursor.execute('UPDATE relationaldb_tournamentparticipant SET predictions = 0, predicted_profit = 0, score = 0')
            cursor.close()
        except Exception as e:
            self.stdout.write(self.style.ERROR(e.message))

    def calculate_scoreboard(self, users_predicted_values):
        """Updates the all the users values and calculates the scoreboard (rankings)"""
        self.stdout.write(self.style.SUCCESS('Starting updating users values {}'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
        # Update users data
        for index, dict_user in enumerate(users_predicted_values):
            try:
                # Atomic update
                with transaction.atomic():
                    user = TournamentParticipant.objects.select_for_update().get(address=dict_user['address'])
                    user.past_rank = user.current_rank
                    user.predicted_profit = dict_user['predicted_profit']
                    user.predictions = dict_user['predictions']
                    user.score = dict_user['score']
                    user.current_rank = index + 1
                    user.diff_rank = user.past_rank - user.current_rank
                    user.save()
            except Exception as e:
                self.stdout.write(self.style.ERROR('Scoreboard Error: Was not possible updating user {} due to: {}'.format(dict_user['address'], e.message)))

        self.stdout.write(self.style.SUCCESS('Users updated successfully'))

    def handle(self, *args, **options):
        """Command entrypoint"""

        users_predicted_values = []
        start_time = datetime.now()
        self.stdout.write(self.style.SUCCESS('Starting Scoreboard process, {}'.format(start_time.strftime("%Y-%m-%d %H:%M:%S"))))

        try:
            # Get the whitelisted markets creators
            whitelisted_creators = TournamentWhitelistedCreator.objects.all().values_list('address', flat=True)
            # Get the whitelisted events
            events = Event.objects.filter(creator__in=whitelisted_creators).values_list('address', flat=True)
            users = TournamentParticipant.objects.filter(
                created__lte=datetime.now() - timedelta(minutes=1)
            ).select_related('tournament_balance')
            users_addresses = users.values_list('address', flat=True)
            all_outcome_token_balances = OutcomeTokenBalance.objects.filter(
                owner__in=users_addresses,
                outcome_token__event__address__in=events
            ).select_related(
                'outcome_token',
                'outcome_token__event',
                'outcome_token__event__categoricalevent',
                'outcome_token__event__scalarevent',
            ).prefetch_related('outcome_token__event__markets')
            all_orders = Order.objects.filter(
                sender__in=users_addresses,
                market__event__address__in=events
            ).prefetch_related('market')

            for user in users:
                # Get balance
                user_address = user.address.lower().replace('0x', '')
                balance = user.tournament_balance.balance
                predicted_value = 0
                predictions = 0  # number of markets the user is participating in

                outcome_token_balances = all_outcome_token_balances.filter(
                    owner=user_address,
                    outcome_token__event__address__in = events,
                    balance__gt=0
                )

                for outcome_token_balance in outcome_token_balances:
                    market = outcome_token_balance.outcome_token.event.markets.first()
                    event = outcome_token_balance.outcome_token.event
                    if event.is_winning_outcome_set:
                        outcome_token_index = outcome_token_balance.outcome_token.index
                        if hasattr(event, 'categoricalevent') and outcome_token_index == event.outcome:
                            predicted_value += outcome_token_balance.balance
                        elif hasattr(event, 'scalarevent'):
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

                            if outcome_token_index == 0:
                                predicted_value += outcome_token_balance.balance * factor_short / OUTCOME_RANGE
                            elif outcome_token_index == 1:
                                predicted_value += outcome_token_balance.balance * factor_long / OUTCOME_RANGE

                    else:
                        order = all_orders.filter(market=market.address, sender=user_address).order_by('-creation_date_time').first()
                        outcome_token_index = order.outcome_token.index
                        marginal_price = order.marginal_prices[outcome_token_index]
                        predicted_value += (outcome_token_balance.balance * marginal_price)

                predictions = all_orders.filter(sender=user_address, market__event__address__in=events).distinct('market').count()

                users_predicted_values.append({
                    'balance': balance,
                    'predicted_profit': predicted_value,
                    'predictions': predictions,
                    'score': predicted_value + balance,
                    'address': user.address
                })

            sorted_scoreboard = sorted(users_predicted_values, key=itemgetter('score'), reverse=True)
            # Calculate scoreboard
            self.calculate_scoreboard(sorted_scoreboard)
        except Exception as e:
            self.stdout.write(self.style.ERROR("Scoreboard Error: {}".format(e.message)))
            raise e
        finally:
            end_time = datetime.now()
            delta = end_time-start_time
            total_seconds = delta.total_seconds()
            benchmark = divmod(total_seconds, 60)
            self.stdout.write(self.style.SUCCESS('Scoreboard calculation took {} minutes and {} seconds'.format(benchmark[0], benchmark[1])))