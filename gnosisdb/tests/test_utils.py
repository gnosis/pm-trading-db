from django.test import TestCase

from relationaldb.tests.factories import (CategoricalEventFactory,
                                          MarketFactory, OutcomeTokenFactory)
from utils import calc_lmsr_marginal_price


class TestUtils(TestCase):

    def test_calc_lmsr_marginal_price(self):
        # outcomeTokenIndex = 0
        # outcomeTokenCount = 1e18
        # create markets
        outcome_token = OutcomeTokenFactory()
        event = outcome_token.event
        market = MarketFactory(event=event)

        net_outcome_tokens_sold = [0, 1]  # market.net_outcome_tokens_sold
        result = calc_lmsr_marginal_price(1, net_outcome_tokens_sold, market.funding)
        self.assertIsNotNone(result)
        self.assertTrue(result > 0)
