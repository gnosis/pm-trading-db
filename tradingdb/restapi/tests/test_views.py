# -*- coding: utf-8 -*-
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from gnosis.utils import add_0x_prefix, generate_eth_account
from tradingdb.relationaldb.models import (CentralizedOracle, Market,
                                           ShortSellOrder,
                                           TournamentParticipant)
from tradingdb.relationaldb.tests.factories import (BuyOrderFactory,
                                                    CategoricalEventFactory,
                                                    CentralizedOracleFactory,
                                                    MarketFactory,
                                                    OutcomeTokenBalanceFactory,
                                                    OutcomeTokenFactory,
                                                    TournamentParticipantBalanceFactory)


class TestViews(APITestCase):

    def test_centralized_oracle(self):
        # test empty centralized-oracles response
        empty_centralized_response = self.client.get(reverse('api:centralized-oracles'), content_type='application/json')
        self.assertEqual(len(empty_centralized_response.json().get('results')), 0)
        # create centralized oracles
        centralized_oracles = [CentralizedOracleFactory() for _ in range(0, 10)]
        centralized_oraclesdb = CentralizedOracle.objects.all()
        self.assertEqual(len(centralized_oracles), centralized_oraclesdb.count())

        centralized_response_data = self.client.get(reverse('api:centralized-oracles'), content_type='application/json')
        self.assertEqual(centralized_response_data.status_code, status.HTTP_200_OK)
        # Check it retrieves the same amount of centralized oracles we created above
        self.assertEqual(len(centralized_response_data.data.get('results')), len(centralized_oracles))

        centralized_search_response = self.client.get(reverse('api:centralized-oracles-by-address', kwargs={
            'oracle_address': centralized_oracles[0].address}), content_type='application/json')
        self.assertEqual(centralized_search_response.status_code, status.HTTP_200_OK)
        self.assertEqual(centralized_search_response.data.get('contract').get('creator'), add_0x_prefix(
            centralized_oracles[0].creator))

        centralized_search_response = self.client.get(reverse('api:centralized-oracles-by-address', kwargs={
            'oracle_address': centralized_oracles[1].address}), content_type='application/json')
        self.assertEqual(centralized_search_response.data.get('contract').get('creator'), add_0x_prefix(
            centralized_oracles[1].creator))

        # test empty not valid addresses - not stored oracle addresses
        centralized_invalid_search_response = self.client.get(reverse('api:centralized-oracles-by-address', kwargs={
            'oracle_address': "abcdef0"}), content_type='application/json')
        self.assertEqual(centralized_invalid_search_response.status_code, status.HTTP_404_NOT_FOUND)

        centralized_invalid_search_response = self.client.get(reverse('api:centralized-oracles-by-address', kwargs={
            'oracle_address': centralized_oracles[0].creator}), content_type='application/json')
        self.assertEqual(centralized_invalid_search_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_events(self):
        # test empty events response
        empty_events_response = self.client.get(reverse('api:events'), content_type='application/json')
        self.assertEqual(len(empty_events_response.json().get('results')), 0)

        oracle = CentralizedOracleFactory()
        event = CategoricalEventFactory(oracle=oracle)

        events_response = self.client.get(reverse('api:events'), content_type='application/json')
        self.assertEqual(len(events_response.data.get('results')), 1)

        event_filtered_response = self.client.get(reverse('api:events-by-address', kwargs={
            'event_address': "abcdef0"}), content_type='application/json')
        self.assertEqual(event_filtered_response.status_code, status.HTTP_404_NOT_FOUND)

        event_filtered_response = self.client.get(reverse('api:events-by-address', kwargs={
            'event_address': event.address}), content_type='application/json')
        self.assertEqual(event_filtered_response.status_code, status.HTTP_200_OK)
        self.assertEqual(events_response.data.get('results')[0].get('contract').get('address'), add_0x_prefix(
            event.address))

    def test_markets(self):
        # test empty events response
        empty_markets_response = self.client.get(reverse('api:markets'), content_type='application/json')
        self.assertEqual(len(empty_markets_response.data.get('results')), 0)

        # create markets
        markets = [MarketFactory() for x in range(0, 10)]
        marketsdb = Market.objects.all()
        self.assertEqual(len(markets), marketsdb.count())

        market_response_data = self.client.get(reverse('api:markets'), content_type='application/json')
        self.assertEqual(market_response_data.status_code, status.HTTP_200_OK)
        self.assertEqual(len(market_response_data.data.get('results')), len(markets))

        market_search_response = self.client.get(reverse('api:markets-by-name', kwargs={
            'market_address': markets[0].address}), content_type='application/json')
        self.assertEqual(market_search_response.status_code, status.HTTP_200_OK)
        self.assertEqual(market_search_response.data.get('contract').get('creator'), add_0x_prefix(markets[0].creator))

        # test empty response
        market_empty_search_response = self.client.get(reverse('api:markets-by-name', kwargs={
            'market_address': "abcdef0"}), content_type='application/json')
        self.assertEqual(market_empty_search_response.status_code, status.HTTP_404_NOT_FOUND)

        market_search_response = self.client.get(reverse('api:markets-by-name', kwargs={
            'market_address': markets[0].address}), content_type='application/json')
        self.assertEqual(market_search_response.status_code, status.HTTP_200_OK)
        self.assertEqual(market_search_response.data.get('contract').get('address'), add_0x_prefix(markets[0].address))

    def test_markets_by_creator(self):
        oracle = CentralizedOracleFactory()
        event = CategoricalEventFactory(oracle=oracle)
        market = MarketFactory(event=event)
        market2 = MarketFactory(event=event)

        url = '{}?creator={}'.format(reverse('api:markets'), market.creator)
        response = self.client.get(url, content_type='application/json')
        self.assertEqual(len(response.data.get('results')), 1)

        url = reverse('api:markets') + '?creator=%s' % market.creator.upper()
        response = self.client.get(url, content_type='application/json')
        self.assertEqual(len(response.data.get('results')), 1)

        url = reverse('api:markets') + '?creator=0x%s,0x%s' % (market.creator.upper(), market2.creator.upper())
        response = self.client.get(url, content_type='application/json')
        self.assertEqual(len(response.data.get('results')), 2)

        # Test with not valid address
        url = reverse('api:markets') + '?creator=%s' % market.creator[:-1]
        response = self.client.get(url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_markets_by_resolution_date(self):
        # test empty events response
        empty_markets_response = self.client.get(reverse('api:markets'), content_type='application/json')
        self.assertEqual(len(empty_markets_response.data.get('results')), 0)

        oracle = CentralizedOracleFactory()
        event = CategoricalEventFactory(oracle=oracle)
        market = MarketFactory(event=event)
        from_date = (timezone.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')

        url = reverse('api:markets') + '?resolution_date_time_after=' + from_date
        correct_date_time_range_response = self.client.get(url, content_type='application/json')
        self.assertEqual(len(correct_date_time_range_response.data.get('results')), 1)

        url = '{}?resolution_date_time_after={}&resolution_date_time_before={}'.format(reverse('api:markets'), from_date, from_date)
        empty_date_time_range_response = self.client.get(url, content_type='application/json')
        self.assertEqual(len(empty_date_time_range_response.data.get('results')), 0)

    def test_markets_by_collateral_token(self):
        oracle = CentralizedOracleFactory()
        event = CategoricalEventFactory(oracle=oracle)
        MarketFactory(event=event)  # create market on database

        url = reverse('api:markets') + '?collateral_token=%s' % event.collateral_token
        response = self.client.get(url, content_type='application/json')
        self.assertEqual(len(response.json().get('results')), 1)

        # test collateral token beginning with 0x
        url = reverse('api:markets') + '?collateral_token=0x%s' % event.collateral_token
        response = self.client.get(url, content_type='application/json')
        self.assertEqual(len(response.json().get('results')), 1)

        wrong_collateral_token = '0x%s' % ('0'*40)
        url = reverse('api:markets') + '?collateral_token=%s' % wrong_collateral_token
        response = self.client.get(url, content_type='application/json')
        self.assertEqual(len(response.json().get('results')), 0)

        # Test with invalid, not ethereum compliant, collateral token
        wrong_collateral_token = event.collateral_token[:-1]
        url = reverse('api:markets') + '?collateral_token=%s' % wrong_collateral_token
        response = self.client.get(url, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_market_trading_volume(self):

        # create markets
        market = MarketFactory()

        market_response = self.client.get(reverse('api:markets'), content_type='application/json')
        self.assertEqual(market_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(market_response.json().get('results')), 1)
        self.assertEqual(market_response.json().get('results')[0]['tradingVolume'], "0")

        market.trading_volume = 12
        market.save()

        market_response_data = self.client.get(reverse('api:markets'), content_type='application/json')
        self.assertEqual(market_response_data.status_code, status.HTTP_200_OK)
        self.assertEqual(len(market_response_data.json().get('results')), 1)

        self.assertEqual(market_response_data.json().get('results')[0]['tradingVolume'], "12")

    def test_market_marginal_prices(self):
        oracle = CentralizedOracleFactory()
        categorical_event = CategoricalEventFactory(oracle=oracle)
        OutcomeTokenFactory(event=categorical_event)  # create outcome token on database
        market = MarketFactory(event=categorical_event)
        sender_address = generate_eth_account(only_address=True)

        # Buy Order
        order_one = BuyOrderFactory(market=market, sender=sender_address)
        market_response = self.client.get(reverse('api:markets-by-name', kwargs={'market_address': market.address}),
                                          content_type='application/json')
        self.assertEqual(market_response.json().get('marginalPrices'), order_one.marginal_prices)

        order_two = BuyOrderFactory(market=market, sender=sender_address)
        market_response = self.client.get(reverse('api:markets-by-name', kwargs={'market_address': market.address}),
                                          content_type='application/json')
        self.assertEqual(market_response.json().get('marginalPrices'), order_two.marginal_prices)

    def test_markets_with_event_description(self):
        # test empty events response
        empty_markets_response = self.client.get(reverse('api:markets'), content_type='application/json')
        self.assertEqual(len(empty_markets_response.json().get('results')), 0)

        # create markets
        oracle = CentralizedOracleFactory()
        event = CategoricalEventFactory(oracle=oracle)
        MarketFactory(event=event)  # create market on database

        market_response_data = self.client.get(reverse('api:markets'), content_type='application/json')
        self.assertEqual(market_response_data.status_code, status.HTTP_200_OK)
        results = market_response_data.json().get('results')
        self.assertEqual(len(results), 1)

        self.assertIsNotNone(results[0]['event']['oracle'].get('eventDescription'))
        self.assertIsNotNone(results[0]['event']['oracle']['eventDescription'].get('ipfsHash'))
        self.assertEqual(results[0]['event']['oracle']['eventDescription']['ipfsHash'], oracle.event_description.ipfs_hash)

    def test_decimal_field_frontier_value(self):
        market = MarketFactory(funding=2 ** 256)
        market_response = self.client.get(reverse('api:markets'), content_type='application/json')
        self.assertEqual(market_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(market_response.json().get('results')), 1)
        self.assertEqual(str(market.funding), market_response.data['results'][0]['funding'])

    def test_shares_by_owner(self):
        market = MarketFactory()
        response = self.client.get(reverse('api:shares-by-owner', kwargs={'market_address': market.address,
                                                                          'owner_address': market.creator}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), 0)

        outcome_token = OutcomeTokenFactory(event=market.event)
        OutcomeTokenFactory(event=market.event)  # create outcome token on database
        OutcomeTokenBalanceFactory(owner=market.creator, outcome_token=outcome_token)
        response = self.client.get(
            reverse('api:shares-by-owner', kwargs={'market_address': market.address, 'owner_address': market.creator}),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), 1)

    def test_all_shares(self):
        market = MarketFactory()
        response = self.client.get(
            reverse('api:all-shares', kwargs={'market_address': market.address}),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), 0)

        outcome_token = OutcomeTokenFactory(event=market.event)
        OutcomeTokenFactory(event=market.event)  # create outcome token on database
        OutcomeTokenBalanceFactory(owner=market.creator, outcome_token=outcome_token)
        response = self.client.get(
            reverse('api:all-shares', kwargs={'market_address': market.address}),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), 1)

    def test_market_trades(self):
        url = reverse('api:trades-by-market', kwargs={'market_address': generate_eth_account(only_address=True)})
        trades_response = self.client.get(url, content_type='application/json')
        self.assertEqual(trades_response.status_code, status.HTTP_404_NOT_FOUND)

        # create markets
        outcome_token = OutcomeTokenFactory()
        event = outcome_token.event
        market = MarketFactory(event=event)
        creation_date_time = timezone.now()

        # Create Order
        order = ShortSellOrder()
        order.creation_date_time = creation_date_time
        order.creation_block = 0
        order.market = market
        order.sender = generate_eth_account(only_address=True)
        order.outcome_token = outcome_token
        order.outcome_token_count = 1
        order.cost = 1
        order.net_outcome_tokens_sold = market.net_outcome_tokens_sold
        order.marginal_prices = ["0.5000", "0.5000"]
        order.save()

        url = reverse('api:trades-by-market', kwargs={'market_address': market.address})
        trades_response = self.client.get(url, content_type='application/json')
        trades_data = trades_response.json()
        self.assertEqual(trades_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(trades_data.get('results')), 1)
        self.assertEqual(trades_data.get('results')[0].get('marginalPrices')[0], order.marginal_prices[0])

        from_date = (creation_date_time - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        to_date = (creation_date_time + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        url = '{}?creation_date_time_after={}&creation_date_time_before={}'.format(reverse('api:trades-by-market',
                                                                                           kwargs={'market_address': market.address}),
                                                                                   from_date,
                                                                                   to_date)
        trades_response = self.client.get(url, content_type='application/json')
        self.assertEqual(trades_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(trades_response.data.get('results')), 1)

        # test querying date with no orders
        from_date = (creation_date_time - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
        to_date = (creation_date_time - timedelta(days=4)).strftime('%Y-%m-%d %H:%M:%S')
        url = '{}?creation_date_time_after={}&creation_date_time_before={}'.format(reverse('api:trades-by-market',
                                                                                           kwargs={'market_address': market.address}),
                                                                                   from_date,
                                                                                   to_date)
        trades_response = self.client.get(url, content_type='application/json')
        self.assertEqual(trades_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(trades_response.data.get('results')), 0)

        # test querying date passing only the from param
        from_date = (creation_date_time - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
        url = reverse('api:trades-by-market',
                      kwargs={'market_address': market.address})
        url += '?creation_date_time_after={}'.format(from_date)
        trades_response = self.client.get(url, content_type='application/json')
        self.assertEqual(trades_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(trades_response.data.get('results')), 1)

    def test_market_trades_unknown_market(self):
        market = MarketFactory()
        url = reverse('api:trades-by-market', kwargs={'market_address': market.address})
        history_data = self.client.get(url, content_type='application/json')
        self.assertEqual(history_data.status_code, status.HTTP_200_OK)
        self.assertEqual(len(history_data.data.get('results')), 0)

    def test_market_participant_history(self):
        outcome_token = OutcomeTokenFactory()
        event = outcome_token.event
        market = MarketFactory(event=event)
        sender_address = generate_eth_account(only_address=True)

        response = self.client.get(
            reverse('api:trades-by-owner', kwargs={'market_address': market.address, 'owner_address': sender_address}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), 0)

        # Create Buy Orders
        BuyOrderFactory(market=market, sender=sender_address)
        BuyOrderFactory(market=market, sender=sender_address)

        response = self.client.get(
            reverse('api:trades-by-owner', kwargs={'market_address': market.address, 'owner_address': sender_address}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), 2)

    def test_trades_by_account(self):
        account1 = generate_eth_account(only_address=True)
        account2 = generate_eth_account(only_address=True)

        url = reverse('api:trades-by-account', kwargs={'account_address': account1})
        empty_trades_response = self.client.get(url, content_type='application/json')
        self.assertEqual(len(empty_trades_response.data.get('results')), 0)

        buy_order = BuyOrderFactory(sender=account1)

        url = reverse('api:trades-by-account', kwargs={'account_address': account1})
        trades_response = self.client.get(url, content_type='application/json')
        self.assertEqual(len(trades_response.data.get('results')), 1)

        url = reverse('api:trades-by-account', kwargs={'account_address': account2})
        no_trades_response = self.client.get(url, content_type='application/json')
        self.assertEqual(len(no_trades_response.data.get('results')), 0)

        # test filter by collateral token
        url = '{}?collateral_token={}'.format(reverse('api:trades-by-account', kwargs={'account_address': account1}),
                                              buy_order.market.event.collateral_token)
        trades_response = self.client.get(url, content_type='application/json')
        self.assertEqual(len(trades_response.data.get('results')), 1)
        # test collateral token beginning with 0x
        url = '{}?collateral_token=0x{}'.format(reverse('api:trades-by-account', kwargs={'account_address': account1}),
                                                buy_order.market.event.collateral_token)
        trades_response = self.client.get(url, content_type='application/json')
        self.assertEqual(len(trades_response.data.get('results')), 1)

        wrong_collateral_token = '0x%s' % (generate_eth_account(only_address=True))
        url = '{}?collateral_token={}'.format(reverse('api:trades-by-account', kwargs={'account_address': account1}),
                                              wrong_collateral_token)
        trades_response = self.client.get(url, content_type='application/json')
        self.assertEqual(len(trades_response.data.get('results')), 0)

    def test_shares_by_account(self):
        account1 = generate_eth_account(only_address=True)
        account2 = generate_eth_account(only_address=True)

        url = reverse('api:shares-by-account', kwargs={'account_address': account1})
        empty_shares_response = self.client.get(url, content_type='application/json')
        self.assertEqual(len(empty_shares_response.data.get('results')), 0)

        oracle = CentralizedOracleFactory()
        event = CategoricalEventFactory(oracle=oracle)
        market = MarketFactory(event=event, creator=account1)
        outcome_token = OutcomeTokenFactory(event=market.event)
        OutcomeTokenBalanceFactory(owner=market.creator, outcome_token=outcome_token)
        BuyOrderFactory(outcome_token=outcome_token, sender=account1, market=market)

        url = reverse('api:shares-by-account', kwargs={'account_address': account1})
        shares_response = self.client.get(url, content_type='application/json')
        decoded_response = shares_response.json()
        self.assertEqual(len(decoded_response.get('results')), 1)
        self.assertEqual(
            decoded_response.get('results')[0].get('eventDescription').get('title'),
            oracle.event_description.title
        )
        self.assertEqual(
            decoded_response.get('results')[0].get('marginalPrice'),
            0.5
        )

        url = reverse('api:shares-by-account', kwargs={'account_address': account2})
        no_shares_response = self.client.get(url, content_type='application/json')
        self.assertEqual(len(no_shares_response.json().get('results')), 0)

        # test filter by collateral token
        url = '{}?collateral_token={}'.format(reverse('api:shares-by-account', kwargs={'account_address': account1}),
                                              event.collateral_token)
        shares_response = self.client.get(url, content_type='application/json')
        self.assertEqual(len(shares_response.json().get('results')), 1)

        # test collateral token beginning with 0x
        url = '{}?collateral_token=0x{}'.format(reverse('api:shares-by-account', kwargs={'account_address': account1}),
                                                event.collateral_token)
        shares_response = self.client.get(url, content_type='application/json')
        self.assertEqual(len(shares_response.json().get('results')), 1)

        wrong_collateral_token = generate_eth_account(only_address=True)
        url = '{}?collateral_token={}'.format(reverse('api:shares-by-account', kwargs={'account_address': account1}),
                                              wrong_collateral_token)
        shares_response = self.client.get(url, content_type='application/json')
        self.assertEqual(len(shares_response.json().get('results')), 0)

    def test_tournament_serializer(self):
        balance = TournamentParticipantBalanceFactory()
        scoreboard_response = self.client.get(reverse('api:scoreboard', kwargs={'account_address': balance.participant.address}),
                                              content_type='application/json')
        self.assertEqual(scoreboard_response.status_code, status.HTTP_200_OK)
        scoreboard_response = self.client.get(reverse('api:scoreboard', kwargs={'account_address': '0x0'}),
                                              content_type='application/json')
        self.assertEqual(scoreboard_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_scoreboard_view(self):
        current_users = TournamentParticipant.objects.all().count()
        scoreboard_response = self.client.get(reverse('api:scoreboard'), content_type='application/json')
        self.assertEqual(scoreboard_response.status_code, status.HTTP_200_OK)
        self.assertEqual(current_users, len(scoreboard_response.data.get('results')))
        balance = TournamentParticipantBalanceFactory()
        scoreboard_response = self.client.get(reverse('api:scoreboard'), content_type='application/json')
        self.assertEqual(scoreboard_response.status_code, status.HTTP_200_OK)
        self.assertEqual(current_users + 1, len(scoreboard_response.data.get('results')))
        balance = TournamentParticipantBalanceFactory()
        scoreboard_response = self.client.get(reverse('api:scoreboard'), content_type='application/json')
        self.assertEqual(scoreboard_response.status_code, status.HTTP_200_OK)
        self.assertEqual(current_users + 2, len(scoreboard_response.data.get('results')))
