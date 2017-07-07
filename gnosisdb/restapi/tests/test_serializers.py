# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from relationaldb.tests.factories import ScalarEventFactory, CategoricalEventFactory, UltimateOracleFactory
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


