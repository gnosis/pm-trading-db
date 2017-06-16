from django.test import TestCase
from eth.address_getters import MarketAddressGetter
from relationaldb.factories import MarketFactory


class TestAddressGetters(TestCase):
    def test_market_address_getter(self):
        getter = MarketAddressGetter()
        market = MarketFactory.create()
        self.assertIsNotNone(market)
        self.assertTrue(getter.contains_address(market.address))
