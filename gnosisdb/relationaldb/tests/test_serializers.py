from unittest import TestCase
from relationaldb.factories import CentralizedOracleFactory

class TestSerializers(TestCase):
    def test_centralized_oracle(self):
        oracle = CentralizedOracleFactory