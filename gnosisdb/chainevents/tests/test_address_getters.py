from django.test import TestCase
from chainevents.address_getters import MarketAddressGetter, EventAddressGetter
from relationaldb.tests.factories import MarketFactory, EventFactory


class TestAddressGetters(TestCase):
    def test_market_address_getter(self):
        getter = MarketAddressGetter()
        self.assertListEqual([], getter.get_addresses())
        market = MarketFactory.create()
        self.assertIsNotNone(market)
        self.assertTrue(getter.__contains__(market.address))
        self.assertListEqual([market.address], getter.get_addresses())
        market2 = MarketFactory.create()
        self.assertListEqual([market.address, market2.address], getter.get_addresses())

    def test_event_address_getter(self):
        getter = EventAddressGetter()
        self.assertListEqual([], getter.get_addresses())
        event = EventFactory.create()
        self.assertIsNotNone(event)
        self.assertTrue(getter.__contains__(event.address))
        self.assertListEqual([event.address], getter.get_addresses())
        event2 = EventFactory.create()
        self.assertListEqual([event.address, event2.address], getter.get_addresses())