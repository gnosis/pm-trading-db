# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from relationaldb.tests.factories import (
    CentralizedOracleFactory, UltimateOracleFactory,
    EventFactory, OutcomeTokenFactory, MarketFactory,
    EventDescriptionFactory, CategoricalEventFactory
)
from relationaldb.models import CentralizedOracle, UltimateOracle, Market
from ipfs.ipfs import Ipfs
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
        self.assertEquals(json.loads(centralized_search_response.content).get('contract').get('creator'), centralized_oracles[0].creator)
        # test empty response
        centralized_empty_search_response = self.client.get(reverse('api:centralized-oracles-by-address', kwargs={'addr': "abcdef0"}), content_type='application/json')
        self.assertEquals(centralized_empty_search_response.status_code, status.HTTP_404_NOT_FOUND)

        centralized_empty_search_response = self.client.get(reverse('api:centralized-oracles-by-address', kwargs={'addr': centralized_oracles[0].creator}), content_type='application/json')
        self.assertEquals(centralized_empty_search_response.status_code, status.HTTP_200_OK)
        self.assertEquals(json.loads(centralized_empty_search_response.content).get('contract').get('creator'), centralized_oracles[0].address)

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
        self.assertEquals(json.loads(ultimate_search_response.content).get('contract').get('creator'), ultimate_oracles[0].creator)
        # test empty response
        ultimate_empty_search_response = self.client.get(reverse('api:ultimate-oracles-by-address', kwargs={'addr': "abcdef0"}), content_type='application/json')
        self.assertEquals(ultimate_empty_search_response.status_code, status.HTTP_404_NOT_FOUND)

        ultimate_search_response = self.client.get(reverse('api:ultimate-oracles-by-address', kwargs={'addr': ultimate_oracles[0].address}), content_type='application/json')
        self.assertEquals(ultimate_search_response.status_code, status.HTTP_200_OK)
        self.assertEquals(json.loads(ultimate_search_response.content).get('contract').get('address'), ultimate_oracles[0].address)

    def test_events(self):
        # test empty events response
        empty_events_response = self.client.get(reverse('api:events'), content_type='application/json')
        self.assertEquals(len(json.loads(empty_events_response.content).get('results')), 0)

        # outcomes creation
        # outcomes = (OutcomeTokenFactory(), OutcomeTokenFactory(), OutcomeTokenFactory())
        # event creation
        event = EventFactory()
        #self.assertEquals(event.outcome_tokens.count(), len(outcomes))
        events_response = self.client.get(reverse('api:events'), content_type='application/json')
        self.assertEquals(len(json.loads(events_response.content).get('results')), 1)

        event_filtered_response = self.client.get(reverse('api:events-by-address', kwargs={'addr': "abcdef0"}), content_type='application/json')
        self.assertEquals(event_filtered_response.status_code, status.HTTP_404_NOT_FOUND)

        event_filtered_response = self.client.get(reverse('api:events-by-address', kwargs={'addr': event.address}), content_type='application/json')
        self.assertEquals(event_filtered_response.status_code, status.HTTP_200_OK)
        self.assertEquals(json.loads(events_response.content).get('results')[0].get('contract').get('address'), event.address)

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
        self.assertEquals(json.loads(market_search_response.content).get('contract').get('creator'), markets[0].creator)
        # test empty response
        market_empty_search_response = self.client.get(reverse('api:markets-by-name', kwargs={'addr': "abcdef0"}), content_type='application/json')
        self.assertEquals(market_empty_search_response.status_code, status.HTTP_404_NOT_FOUND)

        market_search_response = self.client.get(reverse('api:markets-by-name', kwargs={'addr': markets[0].address}), content_type='application/json')
        self.assertEquals(market_search_response.status_code, status.HTTP_200_OK)
        self.assertEquals(json.loads(market_search_response.content).get('contract').get('address'), markets[0].address)

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

    def test_factories(self):
        pass
