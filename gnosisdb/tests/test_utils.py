from unittest import TestCase
from relationaldb.tests.factories import OutcomeTokenFactory, MarketFactory, CategoricalEventFactory
from gnosisdb.utils import calc_lmsr_marginal_price


class TestUtils(TestCase):

    def test_calc_lmsr_marginal_price(self):
        outcomeTokenIndex = 0
        outcomeTokenCount = 1e18
        # create markets
        outcome_token = OutcomeTokenFactory()
        event = outcome_token.event
        market = MarketFactory(event=event)

        net_outcome_tokens_sold = [0, 1] # market.net_outcome_tokens_sold

        # TO BE FIXED
        # result = calc_lmsr_marginal_price(10**18, 1, net_outcome_tokens_sold, market.funding)