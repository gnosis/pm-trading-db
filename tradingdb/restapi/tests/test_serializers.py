# -*- coding: utf-8 -*-
import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tradingdb.relationaldb.tests.factories import (CategoricalEventFactory,
                                                    CentralizedOracleFactory,
                                                    ScalarEventFactory,
                                                    TournamentParticipantBalanceFactory)


class TestSerializers(APITestCase):

    def test_scalar_event_serializer(self):
        oracle = CentralizedOracleFactory()
        event = ScalarEventFactory(oracle=oracle)
        events_response = self.client.get(reverse('api:events'), content_type='application/json')
        self.assertEqual(json.loads(events_response.content).get('results')[0]['type'], 'SCALAR')

    def test_categorical_event_serializer(self):
        oracle = CentralizedOracleFactory()
        event = CategoricalEventFactory(oracle=oracle)
        events_response = self.client.get(reverse('api:events'), content_type='application/json')
        self.assertEqual(json.loads(events_response.content).get('results')[0]['type'], 'CATEGORICAL')

    def test_oracle_types(self):
        centralized_oracle = CentralizedOracleFactory()
        centralized_response = self.client.get(reverse('api:centralized-oracles'), content_type='application/json')
        self.assertEqual(json.loads(centralized_response.content).get('results')[0].get('type'), 'CENTRALIZED')

    def test_tournament_serializer(self):
        participant1 = TournamentParticipantBalanceFactory()
        participant2 = TournamentParticipantBalanceFactory()

        scoreboard_response = self.client.get(reverse('api:scoreboard'), content_type='application/json')
        self.assertEqual(scoreboard_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json.loads(scoreboard_response.content).get('results')), 2)
        self.assertTrue('account' in json.loads(scoreboard_response.content).get('results')[0])
