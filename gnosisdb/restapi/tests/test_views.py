# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from relationaldb.tests.factories import (
    CentralizedOracleFactory, BuyOrderFactory, MarketFactory,
    CategoricalEventFactory, OutcomeTokenFactory, OutcomeTokenBalanceFactory,
    TournamentParticipantBalanceFactory
)
from relationaldb.models import CentralizedOracle, Market, ShortSellOrder, TournamentParticipant
from datetime import datetime, timedelta
from gnosisdb.utils import add_0x_prefix
import json


class TestViews(APITestCase):

    def test_centralized_oracle(self):
        # test empty centralized-oracles response
        empty_centralized_response = self.client.get(reverse('api:centralized-oracles'), content_type='application/json')
        self.assertEquals(len(json.loads(empty_centralized_response.content).get('results')), 0)
        # create centralized oracles
        centralized_oracles = [CentralizedOracleFactory() for x in range(0, 10)]
        centralized_oraclesdb = CentralizedOracle.objects.all()
        self.assertEquals(len(centralized_oracles), centralized_oraclesdb.count())

        centralized_response_data = self.client.get(reverse('api:centralized-oracles'), content_type='application/json')
        self.assertEquals(centralized_response_data.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(centralized_response_data.content).get('results')), len(centralized_oracles))

        centralized_search_response = self.client.get(reverse('api:centralized-oracles-by-address', kwargs={'oracle_address': centralized_oracles[0].address}), content_type='application/json')
        self.assertEquals(centralized_search_response.status_code, status.HTTP_200_OK)
        self.assertEquals(json.loads(centralized_search_response.content).get('contract').get('creator'), add_0x_prefix(centralized_oracles[0].creator))
        # test empty response
        centralized_empty_search_response = self.client.get(reverse('api:centralized-oracles-by-address', kwargs={'oracle_address': "abcdef0"}), content_type='application/json')
        self.assertEquals(centralized_empty_search_response.status_code, status.HTTP_404_NOT_FOUND)

        centralized_empty_search_response = self.client.get(reverse('api:centralized-oracles-by-address', kwargs={'oracle_address': centralized_oracles[0].creator}), content_type='application/json')
        self.assertEquals(centralized_empty_search_response.status_code, status.HTTP_200_OK)
        self.assertEquals(json.loads(centralized_empty_search_response.content).get('contract').get('creator'), add_0x_prefix(centralized_oracles[0].address))

    def test_events(self):
        # test empty events response
        empty_events_response = self.client.get(reverse('api:events'), content_type='application/json')
        self.assertEquals(len(json.loads(empty_events_response.content).get('results')), 0)

        oracle = CentralizedOracleFactory()
        event = CategoricalEventFactory(oracle=oracle)
        # self.assertEquals(event.outcome_tokens.count(), len(outcomes))
        events_response = self.client.get(reverse('api:events'), content_type='application/json')
        self.assertEquals(len(json.loads(events_response.content).get('results')), 1)

        event_filtered_response = self.client.get(reverse('api:events-by-address', kwargs={'event_address': "abcdef0"}), content_type='application/json')
        self.assertEquals(event_filtered_response.status_code, status.HTTP_404_NOT_FOUND)

        event_filtered_response = self.client.get(reverse('api:events-by-address', kwargs={'event_address': event.address}), content_type='application/json')
        self.assertEquals(event_filtered_response.status_code, status.HTTP_200_OK)
        self.assertEquals(json.loads(events_response.content).get('results')[0].get('contract').get('address'), add_0x_prefix(event.address))

    def test_markets(self):
        # test empty events response
        empty_markets_response = self.client.get(reverse('api:markets'), content_type='application/json')
        self.assertEquals(len(json.loads(empty_markets_response.content).get('results')), 0)

        # create markets
        markets = [MarketFactory() for x in range(0, 10)]
        marketsdb = Market.objects.all()
        self.assertEquals(len(markets), marketsdb.count())

        market_response_data = self.client.get(reverse('api:markets'), content_type='application/json')
        self.assertEquals(market_response_data.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(market_response_data.content).get('results')), len(markets))

        market_search_response = self.client.get(reverse('api:markets-by-name', kwargs={'market_address': markets[0].address}), content_type='application/json')
        self.assertEquals(market_search_response.status_code, status.HTTP_200_OK)
        self.assertEquals(json.loads(market_search_response.content).get('contract').get('creator'), add_0x_prefix(markets[0].creator))
        # test empty response
        market_empty_search_response = self.client.get(reverse('api:markets-by-name', kwargs={'market_address': "abcdef0"}), content_type='application/json')
        self.assertEquals(market_empty_search_response.status_code, status.HTTP_404_NOT_FOUND)

        market_search_response = self.client.get(reverse('api:markets-by-name', kwargs={'market_address': markets[0].address}), content_type='application/json')
        self.assertEquals(market_search_response.status_code, status.HTTP_200_OK)
        self.assertEquals(json.loads(market_search_response.content).get('contract').get('address'), add_0x_prefix(markets[0].address))

    def test_markets_by_resolution_date(self):
        # test empty events response
        empty_markets_response = self.client.get(reverse('api:markets'), content_type='application/json')
        self.assertEquals(len(json.loads(empty_markets_response.content).get('results')), 0)

        oracle = CentralizedOracleFactory()
        event = CategoricalEventFactory(oracle=oracle)
        market = MarketFactory(event=event)
        from_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')

        url = reverse('api:markets') + '?resolution_date_time_0=' + from_date
        correct_date_time_range_response = self.client.get(url, content_type='application/json')
        self.assertEquals(len(json.loads(correct_date_time_range_response.content).get('results')), 1)

        url = reverse('api:markets') + '?resolution_date_time_0=' + from_date + '&resolution_date_time_1=' + from_date
        empty_date_time_range_response = self.client.get(url, content_type='application/json')
        self.assertEquals(len(json.loads(empty_date_time_range_response.content).get('results')), 0)

    def test_market_trading_volume(self):

        # create markets
        market = MarketFactory()

        market_response_data = self.client.get(reverse('api:markets'), content_type='application/json')
        self.assertEquals(market_response_data.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(market_response_data.content).get('results')), 1)

        self.assertEqual(json.loads(market_response_data.content)['results'][0]['tradingVolume'], "0")

        market.trading_volume = 12
        market.save()

        market_response_data2 = self.client.get(reverse('api:markets'), content_type='application/json')
        self.assertEquals(market_response_data2.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(market_response_data2.content).get('results')), 1)

        self.assertEqual(json.loads(market_response_data2.content)['results'][0]['tradingVolume'], "12")

    def test_market_marginal_prices(self):
        oracle = CentralizedOracleFactory()
        categorical_event = CategoricalEventFactory(oracle=oracle)
        outcome_token = OutcomeTokenFactory(event=categorical_event)
        market = MarketFactory(event=categorical_event)
        sender_address = '{:040d}'.format(100)

        # Buy Order
        order_one = BuyOrderFactory(market=market, sender=sender_address)
        order_two = BuyOrderFactory(market=market, sender=sender_address)
        market_response = self.client.get(reverse('api:markets-by-name', kwargs={'market_address': market.address}), content_type='application/json')
        market_data = json.loads(market_response.content)
        self.assertEquals(market_data.get('marginalPrices'), order_two.marginal_prices)

    def test_markets_with_event_description(self):
        # test empty events response
        empty_markets_response = self.client.get(reverse('api:markets'), content_type='application/json')
        self.assertEquals(len(json.loads(empty_markets_response.content).get('results')), 0)

        # create markets
        oracle = CentralizedOracleFactory()
        event = CategoricalEventFactory(oracle=oracle)
        market = MarketFactory(event=event)

        market_response_data = self.client.get(reverse('api:markets'), content_type='application/json')
        self.assertEquals(market_response_data.status_code, status.HTTP_200_OK)
        results = json.loads(market_response_data.content).get('results')
        self.assertEquals(len(results), 1)

        self.assertIsNotNone(results[0]['event']['oracle'].get('eventDescription'))
        self.assertIsNotNone(results[0]['event']['oracle']['eventDescription'].get('ipfsHash'))
        self.assertEqual(results[0]['event']['oracle']['eventDescription']['ipfsHash'], oracle.event_description.ipfs_hash)

    def test_decimal_field_frontier_value(self):
        market = MarketFactory()
        market.funding = 2 ** 256
        market.save()

        market_response_data = self.client.get(reverse('api:markets'), content_type='application/json')
        self.assertEquals(market_response_data.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(market_response_data.content).get('results')), 1)

        self.assertEqual(str(market.funding), json.loads(market_response_data.content)['results'][0]['funding'])

    def test_shares_by_owner(self):
        market = MarketFactory()
        response = self.client.get(reverse('api:shares-by-owner', kwargs = {'market_address': market.address, 'owner_address': market.creator}),
                                   content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(response.content).get('results')), 0)

        outcome_token = OutcomeTokenFactory(event=market.event)
        outcome_token2 = OutcomeTokenFactory(event=market.event)
        OutcomeTokenBalanceFactory(owner=market.creator, outcome_token=outcome_token)
        response = self.client.get(
            reverse('api:shares-by-owner', kwargs={'market_address': market.address, 'owner_address': market.creator}),
            content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(response.content).get('results')), 1)

    def test_all_shares(self):
        market = MarketFactory()
        response = self.client.get(
            reverse('api:all-shares', kwargs={'market_address': market.address}),
            content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(response.content).get('results')), 0)

        outcome_token = OutcomeTokenFactory(event=market.event)
        outcome_token2 = OutcomeTokenFactory(event=market.event)
        OutcomeTokenBalanceFactory(owner=market.creator, outcome_token=outcome_token)
        response = self.client.get(
            reverse('api:all-shares', kwargs={'market_address': market.address}),
            content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(response.content).get('results')), 1)

    def test_market_trades(self):
        url = reverse('api:trades-by-market', kwargs={'market_address': '{:040d}'.format(1000)})
        trades_response = self.client.get(url, content_type='application/json')
        self.assertEquals(trades_response.status_code, status.HTTP_404_NOT_FOUND)

        # create markets
        outcome_token = OutcomeTokenFactory()
        event = outcome_token.event
        oracle = event.oracle
        market = MarketFactory(event=event)
        creation_date_time = datetime.now()

        # Create Order
        order = ShortSellOrder()
        order.creation_date_time = creation_date_time
        order.creation_block = 0
        order.market = market
        order.sender = '0x1'
        order.outcome_token = outcome_token
        order.outcome_token_count = 1
        order.cost = 1
        order.net_outcome_tokens_sold = market.net_outcome_tokens_sold
        order.marginal_prices = ["0.5000", "0.5000"]
        order.save()

        url = reverse('api:trades-by-market', kwargs={'market_address': market.address})

        trades_response = self.client.get(url, content_type='application/json')
        trades_data = json.loads(trades_response.content)
        self.assertEquals(trades_response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(trades_data.get('results')), 1)
        self.assertEquals(trades_data.get('results')[0].get('marginalPrices')[0], order.marginal_prices[0])

        from_date = (creation_date_time - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        to_date = (creation_date_time + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        url = reverse('api:trades-by-market',
                      kwargs={'market_address': market.address})
        url += '?creation_date_time_0=' + from_date + '&creation_date_time_1='+to_date
        trades_response = self.client.get(url, content_type='application/json')
        self.assertEquals(trades_response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(trades_response.content).get('results')), 1)

        # test querying date with no orders
        from_date = (creation_date_time - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
        to_date = (creation_date_time - timedelta(days=4)).strftime('%Y-%m-%d %H:%M:%S')
        url = reverse('api:trades-by-market',
                      kwargs={'market_address': market.address})
        url += '?creation_date_time_0=' + from_date + '&creation_date_time_1=' + to_date
        trades_response = self.client.get(url, content_type='application/json')
        self.assertEquals(trades_response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(trades_response.content).get('results')), 0)

        # test querying date passing only the from param
        from_date = (creation_date_time - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
        url = reverse('api:trades-by-market',
                      kwargs={'market_address': market.address})
        url += '?creation_date_time_0=' + from_date
        trades_response = self.client.get(url, content_type='application/json')
        self.assertEquals(trades_response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(trades_response.content).get('results')), 1)

    def test_market_trades_unknown_market(self):
        market = MarketFactory()
        url = reverse('api:trades-by-market', kwargs={'market_address': market.address})
        history_data = self.client.get(url, content_type='application/json')
        self.assertEquals(history_data.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(history_data.content).get('results')), 0)

    def test_market_participant_history(self):
        outcome_token = OutcomeTokenFactory()
        event = outcome_token.event
        oracle = event.oracle
        market = MarketFactory(event=event)
        creation_date_time = datetime.now()
        sender_address = '{:040d}'.format(100)

        response = self.client.get(
            reverse('api:trades-by-owner', kwargs={'market_address': market.address, 'owner_address': sender_address}),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(response.content).get('results')), 0)

        # Buy Order
        BuyOrderFactory(market=market, sender=sender_address)
        BuyOrderFactory(market=market, sender=sender_address)

        response = self.client.get(
            reverse('api:trades-by-owner', kwargs={'market_address': market.address, 'owner_address': sender_address}),
            content_type='application/json'
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(response.content).get('results')), 2)

    def test_trades_by_account(self):
        account1 = '{:040d}'.format(13)
        account2 = '{:040d}'.format(14)

        url = reverse('api:trades-by-account', kwargs={'account_address': account1})
        empty_trades_response = self.client.get(url, content_type='application/json')
        self.assertEquals(len(json.loads(empty_trades_response.content).get('results')), 0)

        BuyOrderFactory(sender=account1)

        url = reverse('api:trades-by-account', kwargs={'account_address': account1})
        trades_response = self.client.get(url, content_type='application/json')
        self.assertEquals(len(json.loads(trades_response.content).get('results')), 1)

        url = reverse('api:trades-by-account', kwargs={'account_address': account2})
        no_trades_response = self.client.get(url, content_type='application/json')
        self.assertEquals(len(json.loads(no_trades_response.content).get('results')), 0)

    def test_shares_by_account(self):
        account1 = '{:040d}'.format(13)
        account2 = '{:040d}'.format(14)

        url = reverse('api:shares-by-account', kwargs={'account_address': account1})
        empty_shares_response = self.client.get(url, content_type='application/json')
        self.assertEquals(len(json.loads(empty_shares_response.content).get('results')), 0)

        oracle = CentralizedOracleFactory()
        event = CategoricalEventFactory(oracle=oracle)
        market = MarketFactory(event=event, creator=account1)
        outcome_token = OutcomeTokenFactory(event=market.event)
        OutcomeTokenBalanceFactory(owner=market.creator, outcome_token=outcome_token)
        BuyOrderFactory(outcome_token=outcome_token, sender=account1, market=market)

        url = reverse('api:shares-by-account', kwargs={'account_address': account1})
        shares_response = self.client.get(url, content_type='application/json')
        decoded_response = json.loads(shares_response.content)
        self.assertEquals(len(decoded_response.get('results')), 1)
        self.assertEquals(
            decoded_response.get('results')[0].get('eventDescription').get('title'),
            oracle.event_description.title
        )
        self.assertEquals(
            decoded_response.get('results')[0].get('marginalPrice'),
            0.5
        )

        url = reverse('api:shares-by-account', kwargs={'account_address': account2})
        no_shares_response = self.client.get(url, content_type='application/json')
        self.assertEquals(len(json.loads(no_shares_response.content).get('results')), 0)

    def test_tournament_serializer(self):
        balance = TournamentParticipantBalanceFactory()
        scoreboard_response = self.client.get(reverse('api:scoreboard', kwargs={'account_address': balance.participant.address}), content_type='application/json')
        self.assertEquals(scoreboard_response.status_code, status.HTTP_200_OK)
        scoreboard_response = self.client.get(reverse('api:scoreboard', kwargs={'account_address': '0x0'}), content_type='application/json')
        self.assertEquals(scoreboard_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_scoreboard_view(self):
        current_users = TournamentParticipant.objects.all().count()
        scoreboard_response = self.client.get(reverse('api:scoreboard'), content_type='application/json')
        self.assertEquals(scoreboard_response.status_code, status.HTTP_200_OK)
        self.assertEqual(current_users, len(json.loads(scoreboard_response.content)['results']))
        balance = TournamentParticipantBalanceFactory()
        scoreboard_response = self.client.get(reverse('api:scoreboard'), content_type='application/json')
        self.assertEquals(scoreboard_response.status_code, status.HTTP_200_OK)
        self.assertEqual(current_users + 1, len(json.loads(scoreboard_response.content)['results']))
        balance = TournamentParticipantBalanceFactory()
        scoreboard_response = self.client.get(reverse('api:scoreboard'), content_type='application/json')
        self.assertEquals(scoreboard_response.status_code, status.HTTP_200_OK)
        self.assertEqual(current_users + 2, len(json.loads(scoreboard_response.content)['results']))