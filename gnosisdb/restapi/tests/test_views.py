# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from relationaldb.tests.factories import (
    CentralizedOracleFactory, UltimateOracleFactory, BuyOrderFactory,
    MarketFactory, CategoricalEventFactory, OutcomeTokenFactory, OutcomeTokenBalanceFactory
)
from relationaldb.models import CentralizedOracle, UltimateOracle, Market, ShortSellOrder, BuyOrder
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

        centralized_search_response = self.client.get(reverse('api:centralized-oracles-by-address', kwargs={'addr': centralized_oracles[0].address}), content_type='application/json')
        self.assertEquals(centralized_search_response.status_code, status.HTTP_200_OK)
        self.assertEquals(json.loads(centralized_search_response.content).get('contract').get('creator'), add_0x_prefix(centralized_oracles[0].creator))
        # test empty response
        centralized_empty_search_response = self.client.get(reverse('api:centralized-oracles-by-address', kwargs={'addr': "abcdef0"}), content_type='application/json')
        self.assertEquals(centralized_empty_search_response.status_code, status.HTTP_404_NOT_FOUND)

        centralized_empty_search_response = self.client.get(reverse('api:centralized-oracles-by-address', kwargs={'addr': centralized_oracles[0].creator}), content_type='application/json')
        self.assertEquals(centralized_empty_search_response.status_code, status.HTTP_200_OK)
        self.assertEquals(json.loads(centralized_empty_search_response.content).get('contract').get('creator'), add_0x_prefix(centralized_oracles[0].address))

    def test_ultimate_oracle(self):
        # test empty ultimate-oracles response
        empty_ultimate_response = self.client.get(reverse('api:ultimate-oracles'), content_type='application/json')
        self.assertEquals(len(json.loads(empty_ultimate_response.content).get('results')), 0)

        # create ultimate oracles
        ultimate_oracles = [UltimateOracleFactory() for x in range(0, 10)]
        ultimate_oraclesdb = UltimateOracle.objects.all()
        self.assertEquals(len(ultimate_oracles), ultimate_oraclesdb.count())

        ultimate_response_data = self.client.get(reverse('api:ultimate-oracles'), content_type='application/json')
        self.assertEquals(ultimate_response_data.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(ultimate_response_data.content).get('results')), len(ultimate_oracles))

        ultimate_search_response = self.client.get(reverse('api:ultimate-oracles-by-address', kwargs={'addr': ultimate_oracles[0].address}), content_type='application/json')
        self.assertEquals(ultimate_search_response.status_code, status.HTTP_200_OK)
        self.assertEquals(json.loads(ultimate_search_response.content).get('contract').get('creator'), add_0x_prefix(ultimate_oracles[0].creator))
        # test empty response
        ultimate_empty_search_response = self.client.get(reverse('api:ultimate-oracles-by-address', kwargs={'addr': "abcdef0"}), content_type='application/json')
        self.assertEquals(ultimate_empty_search_response.status_code, status.HTTP_404_NOT_FOUND)

        ultimate_search_response = self.client.get(reverse('api:ultimate-oracles-by-address', kwargs={'addr': ultimate_oracles[0].address}), content_type='application/json')
        self.assertEquals(ultimate_search_response.status_code, status.HTTP_200_OK)
        self.assertEquals(json.loads(ultimate_search_response.content).get('contract').get('address'), add_0x_prefix(ultimate_oracles[0].address))

    def test_events(self):
        # test empty events response
        empty_events_response = self.client.get(reverse('api:events'), content_type='application/json')
        self.assertEquals(len(json.loads(empty_events_response.content).get('results')), 0)

        # outcomes creation
        # outcomes = (OutcomeTokenFactory(), OutcomeTokenFactory(), OutcomeTokenFactory())
        # event creation
        event = CategoricalEventFactory()
        # self.assertEquals(event.outcome_tokens.count(), len(outcomes))
        events_response = self.client.get(reverse('api:events'), content_type='application/json')
        self.assertEquals(len(json.loads(events_response.content).get('results')), 1)

        event_filtered_response = self.client.get(reverse('api:events-by-address', kwargs={'addr': "abcdef0"}), content_type='application/json')
        self.assertEquals(event_filtered_response.status_code, status.HTTP_404_NOT_FOUND)

        event_filtered_response = self.client.get(reverse('api:events-by-address', kwargs={'addr': event.address}), content_type='application/json')
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

        market_search_response = self.client.get(reverse('api:markets-by-name', kwargs={'addr': markets[0].address}), content_type='application/json')
        self.assertEquals(market_search_response.status_code, status.HTTP_200_OK)
        self.assertEquals(json.loads(market_search_response.content).get('contract').get('creator'), add_0x_prefix(markets[0].creator))
        # test empty response
        market_empty_search_response = self.client.get(reverse('api:markets-by-name', kwargs={'addr': "abcdef0"}), content_type='application/json')
        self.assertEquals(market_empty_search_response.status_code, status.HTTP_404_NOT_FOUND)

        market_search_response = self.client.get(reverse('api:markets-by-name', kwargs={'addr': markets[0].address}), content_type='application/json')
        self.assertEquals(market_search_response.status_code, status.HTTP_200_OK)
        self.assertEquals(json.loads(market_search_response.content).get('contract').get('address'), add_0x_prefix(markets[0].address))

    def test_market_trading_volume(self):

        # create markets
        market = MarketFactory()

        market_response_data = self.client.get(reverse('api:markets'), content_type='application/json')
        self.assertEquals(market_response_data.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(market_response_data.content).get('results')), 1)

        self.assertEqual(json.loads(market_response_data.content)['results'][0]['tradingVolume'], "0")

        BuyOrderFactory(market=market, cost=12)

        market_response_data2 = self.client.get(reverse('api:markets'), content_type='application/json')
        self.assertEquals(market_response_data2.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(market_response_data2.content).get('results')), 1)

        self.assertEqual(json.loads(market_response_data2.content)['results'][0]['tradingVolume'], "12")

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
        OutcomeTokenBalanceFactory(owner=market.creator, outcome_token=outcome_token)
        response = self.client.get(
            reverse('api:all-shares', kwargs={'market_address': market.address}),
            content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(response.content).get('results')), 1)

    def test_market_history(self):
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
        order.save()

        url = reverse('api:history-by-market') + '?market=' + market.address
        history_data = self.client.get(url, content_type='application/json')
        self.assertEquals(history_data.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(history_data.content).get('results')), 1)

        from_date = (creation_date_time - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        to_date = (creation_date_time + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        url = reverse('api:history-by-market') + '?market=' + market.address + '&from=' + from_date + '&to=' + to_date
        history_data = self.client.get(url, content_type='application/json')
        self.assertEquals(history_data.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(history_data.content).get('results')), 1)

        # test querying date with no orders
        from_date = (creation_date_time - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
        to_date = (creation_date_time - timedelta(days=4)).strftime('%Y-%m-%d %H:%M:%S')
        url =  reverse('api:history-by-market') + '?market=' + market.address + '&from=' + from_date + '&to=' + to_date
        history_data = self.client.get(url, content_type='application/json')
        self.assertEquals(history_data.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(history_data.content).get('results')), 0)

        # test querying date passing only the from param
        from_date = (creation_date_time - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
        url =  reverse('api:history-by-market') + '?market=' + market.address + '&from=' + from_date
        history_data = self.client.get(url, content_type='application/json')
        self.assertEquals(history_data.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(history_data.content).get('results')), 1)

    def test_history_unknown_market(self):
        market = MarketFactory()
        url = reverse('api:history-by-market') + '?market=' + market.address
        history_data = self.client.get(url, content_type='application/json')
        self.assertEquals(history_data.status_code, status.HTTP_404_NOT_FOUND)

    def test_history_without_market(self):
        url = reverse('api:history-by-market')
        history_data = self.client.get(url, content_type='application/json')
        self.assertEquals(history_data.status_code, status.HTTP_400_BAD_REQUEST)

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