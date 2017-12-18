# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from relationaldb.tests.factories import (
    ScalarEventFactory, CategoricalEventFactory, CentralizedOracleFactory, TournamentParticipantBalanceFactory
)
import json


class TestSerializers(APITestCase):

    def test_scalar_event_serializer(self):
        oracle = CentralizedOracleFactory()
        event = ScalarEventFactory(oracle=oracle)
        events_response = self.client.get(reverse('api:events'), content_type='application/json')
        self.assertEquals(json.loads(events_response.content).get('results')[0]['type'], 'SCALAR')

    def test_categorical_event_serializer(self):
        oracle = CentralizedOracleFactory()
        event = CategoricalEventFactory(oracle=oracle)
        events_response = self.client.get(reverse('api:events'), content_type='application/json')
        self.assertEquals(json.loads(events_response.content).get('results')[0]['type'], 'CATEGORICAL')

    def test_oracle_types(self):
        centralized_oracle = CentralizedOracleFactory()
        centralized_response = self.client.get(reverse('api:centralized-oracles'), content_type='application/json')
        self.assertEquals(json.loads(centralized_response.content).get('results')[0].get('type'), 'CENTRALIZED')

    def test_tournament_serializer(self):
        participant1 = TournamentParticipantBalanceFactory()
        participant2 = TournamentParticipantBalanceFactory()

        scoreboard_response = self.client.get(reverse('api:scoreboard'), content_type='application/json')
        self.assertEquals(scoreboard_response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(scoreboard_response.content).get('results')), 2)
        self.assertTrue('account' in json.loads(scoreboard_response.content).get('results')[0])
