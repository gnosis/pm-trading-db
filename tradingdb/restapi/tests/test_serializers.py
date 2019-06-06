# -*- coding: utf-8 -*-
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
        ScalarEventFactory(oracle=oracle)  # create event on database
        events_response = self.client.get(reverse('api:events'), content_type='application/json')
        self.assertEqual(events_response.data.get('results')[0]['type'], 'SCALAR')

    def test_categorical_event_serializer(self):
        oracle = CentralizedOracleFactory()
        CategoricalEventFactory(oracle=oracle)  # create event on database
        events_response = self.client.get(reverse('api:events'), content_type='application/json')
        self.assertEqual(events_response.data.get('results')[0]['type'], 'CATEGORICAL')

    def test_oracle_types(self):
        CentralizedOracleFactory()  # create oracle on database
        centralized_response = self.client.get(reverse('api:centralized-oracles'), content_type='application/json')
        self.assertEqual(centralized_response.data.get('results')[0].get('type'), 'CENTRALIZED')

    def test_tournament_serializer(self):
        # Create participants on database
        TournamentParticipantBalanceFactory()
        TournamentParticipantBalanceFactory()

        scoreboard_response = self.client.get(reverse('api:scoreboard'), content_type='application/json')
        self.assertEqual(scoreboard_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(scoreboard_response.data.get('results')), 2)
        self.assertTrue('account' in scoreboard_response.data.get('results')[0])
