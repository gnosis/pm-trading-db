# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from relationaldb.tests.factories import (
    ScalarEventFactory, CategoricalEventFactory, UltimateOracleFactory, CentralizedOracleFactory,
    TournamentParticipantFactory
)
import json


class TestSerializers(APITestCase):

    def test_scalar_event_serializer(self):
        event = ScalarEventFactory()
        events_response = self.client.get(reverse('api:events'), content_type='application/json')
        self.assertEquals(json.loads(events_response.content).get('results')[0]['type'], 'SCALAR')

    def test_categorical_event_serializer(self):
        event = CategoricalEventFactory()
        events_response = self.client.get(reverse('api:events'), content_type='application/json')
        self.assertEquals(json.loads(events_response.content).get('results')[0]['type'], 'CATEGORICAL')

    def test_null_values_in_response(self):
        oracle = UltimateOracleFactory(forwarded_oracle=None)
        response = self.client.get(reverse('api:ultimate-oracles'), content_type='application/json')
        self.assertFalse(json.loads(response.content).get('results')[0].get('forwardedOracle', False))

    def test_oracle_types(self):
        ultimate_oracle = UltimateOracleFactory(forwarded_oracle=None)
        centralized_oracle = CentralizedOracleFactory()
        ultimate_response = self.client.get(reverse('api:ultimate-oracles'), content_type='application/json')
        centralized_response = self.client.get(reverse('api:centralized-oracles'), content_type='application/json')
        self.assertEquals(json.loads(ultimate_response.content).get('results')[0].get('type'), 'ULTIMATE')
        self.assertEquals(json.loads(centralized_response.content).get('results')[0].get('type'), 'CENTRALIZED')

    def test_tournament_serializer(self):
        participant1 = TournamentParticipantFactory()
        participant2 = TournamentParticipantFactory()

        scoreboard_response = self.client.get(reverse('api:scoreboard'), content_type='application/json')
        self.assertEquals(scoreboard_response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(json.loads(scoreboard_response.content).get('results')), 2)