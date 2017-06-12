from django.test import TestCase
from relationaldb.factories import CentralizedOracleFactory


class TestModels(TestCase):

    def test_centralized_oracle(self):
        oracle = CentralizedOracleFactory()
        self.assertIsNotNone(oracle.pk)