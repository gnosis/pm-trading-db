# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from relationaldb.factories import CentralizedOracleFactory, UltimateOracleFactory
from relationaldb.models import CentralizedOracle, UltimateOracle
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
