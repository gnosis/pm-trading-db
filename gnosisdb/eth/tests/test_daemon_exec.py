# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from web3 import Web3
from eth.factories import DaemonFactory
from eth.event_listener import EventListener
from eth.web3_service import Web3Service
from web3 import TestRPCProvider
from json import loads, dumps
from relationaldb import models
from ipfs.ipfs import Ipfs
from relationaldb.factories import EventDescriptionFactory
import os



centralized_oracle_abi = loads('[{"constant":false,"inputs":[{"name":"ipfsHash","type":"bytes"}],"name":"createCentralizedOracle",'
            '"outputs":[{"name":"centralizedOracle","type":"address"}],"payable":false,"type":"function"},'
            '{"anonymous":false,"inputs":[{"indexed":true,"name":"creator","type":"address"},{"indexed":false,'
            '"name":"centralizedOracle","type":"address"},{"indexed":false,"name":"ipfsHash","type":"bytes"}],'
            '"name":"CentralizedOracleCreation","type":"event"}]')

ultimate_oracle_abi = loads('[{"inputs": [{"type": "address", "name": "oracle"}, {"type": "address", "name": "collateralToken"},'
                            '{"type": "uint8", "name": "spreadMultiplier"}, {"type": "uint256", "name": "challengePeriod"},'
                            '{"type": "uint256", "name": "challengeAmount"}, {"type": "uint256", "name": "frontRunnerPeriod"}],'
                            '"constant": false, "name": "createUltimateOracle", "payable": false, "outputs": [{"type": "address",'
                            '"name": "ultimateOracle"}], "type": "function"}, {"inputs": [{"indexed": true, "type": "address",'
                            '"name": "creator"}, {"indexed": false, "type": "address", "name": "ultimateOracle"}, {"indexed":'
                            'false, "type": "address", "name": "oracle"}, {"indexed": false, "type": "address", "name":'
                            '"collateralToken"}, {"indexed": false, "type": "uint8", "name": "spreadMultiplier"},'
                            '{"indexed": false, "type": "uint256", "name": "challengePeriod"}, {"indexed": false, "type":'
                            '"uint256", "name": "challengeAmount"}, {"indexed": false, "type": "uint256", "name":'
                            '"frontRunnerPeriod"}], "type": "event", "name": "UltimateOracleCreation", "anonymous": false}]')

ether_token_abi = loads('[{"inputs": [], "constant": true, "name": "name", "payable": false, "outputs": [{"type": "string",'
                        '"name": ""}], "type": "function"}, {"inputs": [{"type": "address", "name": "spender"}, '
                        '{"type": "uint256", "name": "value"}], "constant": false, "name": "approve", "payable": false,'
                        '"outputs": [{"type": "bool", "name": ""}], "type": "function"}, {"inputs": [], "constant": true,'
                        '"name": "totalSupply", "payable": false, "outputs": [{"type": "uint256", "name": ""}],'
                        '"type": "function"}, {"inputs": [{"type": "address", "name": "from"}, {"type": "address",'
                        '"name": "to"}, {"type": "uint256", "name": "value"}], "constant": false, "name": "transferFrom",'
                        '"payable": false, "outputs": [{"type": "bool", "name": ""}], "type": "function"}, {"inputs":'
                        '[{"type": "uint256", "name": "value"}], "constant": false, "name": "withdraw", "payable": false,'
                        '"outputs": [], "type": "function"}, {"inputs": [], "constant": true, "name": "decimals",'
                        '"payable": false, "outputs": [{"type": "uint8", "name": ""}], "type": "function"},'
                        '{"inputs": [{"type": "address", "name": "owner"}], "constant": true, "name": "balanceOf",'
                        '"payable": false, "outputs": [{"type": "uint256", "name": ""}], "type": "function"},'
                        '{"inputs": [], "constant": true, "name": "symbol", "payable": false, "outputs": [{"type":'
                        '"string", "name": ""}], "type": "function"}, {"inputs": [{"type": "address", "name": "to"},'
                        '{"type": "uint256", "name": "value"}], "constant": false, "name": "transfer", "payable": false,'
                        '"outputs": [{"type": "bool", "name": ""}], "type": "function"}, {"inputs": [], "constant": false,'
                        '"name": "deposit", "payable": true, "outputs": [], "type": "function"}, {"inputs": [{"type":'
                        '"address", "name": "owner"}, {"type": "address", "name": "spender"}], "constant": true, "name":'
                        '"allowance", "payable": false, "outputs": [{"type": "uint256", "name": ""}], "type": "function"},'
                        '{"inputs": [{"indexed": true, "type": "address", "name": "sender"}, {"indexed": false, "type":'
                        '"uint256", "name": "value"}], "type": "event", "name": "Deposit", "anonymous": false}, {"inputs":'
                        '[{"indexed": true, "type": "address", "name": "receiver"}, {"indexed": false, "type": "uint256",'
                        '"name": "value"}], "type": "event", "name": "Withdrawal", "anonymous": false}, {"inputs":'
                        '[{"indexed": true, "type": "address", "name": "from"}, {"indexed": true, "type": "address",'
                        '"name": "to"}, {"indexed": false, "type": "uint256", "name": "value"}], "type": "event",'
                        '"name": "Transfer", "anonymous": false}, {"inputs": [{"indexed": true, "type": "address",'
                        '"name": "owner"}, {"indexed": true, "type": "address", "name": "spender"}, {"indexed": false,'
                        '"type": "uint256", "name": "value"}], "type": "event", "name": "Approval", "anonymous": false}]')

event_factory_abi = loads('[{"inputs": [{"type": "address", "name": "collateralToken"}, {"type": "address", "name": "oracle"},'
                          '{"type": "int256", "name": "lowerBound"}, {"type": "int256", "name": "upperBound"}], "constant":'
                          'false, "name": "createScalarEvent", "payable": false, "outputs": [{"type": "address", "name":'
                          '"eventContract"}], "type": "function"}, {"inputs": [{"type": "bytes32", "name": ""}], "constant":'
                          'true, "name": "categoricalEvents", "payable": false, "outputs": [{"type": "address", "name": ""}],'
                          '"type": "function"}, {"inputs": [{"type": "bytes32", "name": ""}], "constant": true, "name":'
                          '"scalarEvents", "payable": false, "outputs": [{"type": "address", "name": ""}], "type": "function"},'
                          '{"inputs": [{"type": "address", "name": "collateralToken"}, {"type": "address", "name": "oracle"},'
                          '{"type": "uint8", "name": "outcomeCount"}], "constant": false, "name": "createCategoricalEvent",'
                          '"payable": false, "outputs": [{"type": "address", "name": "eventContract"}], "type": "function"},'
                          '{"inputs": [{"indexed": true, "type": "address", "name": "creator"}, {"indexed": false, "type":'
                          '"address", "name": "categoricalEvent"}, {"indexed": false, "type": "address", "name":'
                          '"collateralToken"}, {"indexed": false, "type": "address", "name": "oracle"}, {"indexed": false,'
                          '"type": "uint8", "name": "outcomeCount"}], "type": "event", "name": "CategoricalEventCreation",'
                          '"anonymous": false}, {"inputs": [{"indexed": true, "type": "address", "name": "creator"},'
                          '{"indexed": false, "type": "address", "name": "scalarEvent"}, {"indexed": false, "type": "address",'
                          '"name": "collateralToken"}, {"indexed": false, "type": "address", "name": "oracle"},'
                          '{"indexed": false, "type": "int256", "name": "lowerBound"}, {"indexed": false, "type": "int256",'
                          '"name": "upperBound"}], "type": "event", "name": "ScalarEventCreation", "anonymous": false}]')

market_factory_abi = loads('[{"inputs": [{"type": "address", "name": "market"}, {"type": "uint8", "name": "outcomeTokenIndex"},'
                           '{"type": "uint256", "name": "outcomeTokenCount"}], "constant": true, "name": "calcProfit", "payable":'
                           'false, "outputs": [{"type": "uint256", "name": "profit"}], "type": "function"}, {"inputs":'
                           '[{"type": "address", "name": "market"}, {"type": "uint8", "name": "outcomeTokenIndex"},'
                           '{"type": "uint256", "name": "outcomeTokenCount"}], "constant": true, "name": "calcCost",'
                           '"payable": false, "outputs": [{"type": "uint256", "name": "cost"}], "type": "function"},'
                           '{"inputs": [{"type": "address", "name": "market"}, {"type": "uint8", "name": "outcomeTokenIndex"}],'
                           '"constant": true, "name": "calcMarginalPrice", "payable": false, "outputs": [{"type":'
                           '"uint256", "name": "price"}], "type": "function"}]')


centralized_oracle_bytecode = "6060604052341561000c57fe5b5b6109ad8061001c6000396000f30060606040526000357c01000000000000000000000000000000" \
          "00000000000000000000000000900463ffffffff1680634e2f220c1461003b575bfe5b341561004357fe5b61009360048080359060" \
          "2001908201803590602001908080601f01602080910402602001604051908101604052809392919081815260200183838082843782" \
          "0191505050505050919050506100d5565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffff" \
          "ffffffffffffffffffffffff16815260200191505060405180910390f35b600033826100e16102a1565b808373ffffffffffffffff" \
          "ffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200180602001828103825283818151" \
          "81526020019150805190602001908083836000831461015f575b80518252602083111561015f576020820191506020810190506020" \
          "8303925061013b565b505050905090810190601f16801561018b5780820380516001836020036101000a031916815260200191505b" \
          "509350505050604051809103906000f08015156101a457fe5b90503373ffffffffffffffffffffffffffffffffffffffff167f33a1" \
          "926cf5c2f7306ac1685bf19260d678fea874f5f59c00b69fa5e2643ecfd28284604051808373ffffffffffffffffffffffffffffff" \
          "ffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018060200182810382528381815181526020019150" \
          "8051906020019080838360008314610261575b8051825260208311156102615760208201915060208101905060208303925061023d" \
          "565b505050905090810190601f16801561028d5780820380516001836020036101000a031916815260200191505b50935050505060" \
          "405180910390a25b919050565b6040516106d0806102b28339019056006060604052341561000c57fe5b6040516106d03803806106" \
          "d0833981016040528080519060200190919080518201919050505b602e81511415156100435760006000fd5b81600060006101000a" \
          "81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff160217" \
          "905550806001908051906020019061009a9291906100a3565b505b5050610148565b82805460018160011615610100020316600290" \
          "0490600052602060002090601f016020900481019282601f106100e457805160ff1916838001178555610112565b82800160010185" \
          "558215610112579182015b828111156101115782518255916020019190600101906100f6565b5b50905061011f9190610123565b50" \
          "90565b61014591905b80821115610141576000816000905550600101610129565b5090565b90565b610579806101576000396000f3" \
          "006060604052361561008c576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16" \
          "806327793f871461008e578063717a195a146100b45780637e7e4b47146100d45780638da5cb5b146100fa578063a39a45b7146101" \
          "4c578063c623674f14610182578063c65fb3801461021b578063ccdf68f314610245575bfe5b341561009657fe5b61009e61026f56" \
          "5b6040518082815260200191505060405180910390f35b34156100bc57fe5b6100d26004808035906020019091905050610275565b" \
          "005b34156100dc57fe5b6100e461034d565b6040518082815260200191505060405180910390f35b341561010257fe5b61010a6103" \
          "58565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681" \
          "5260200191505060405180910390f35b341561015457fe5b610180600480803573ffffffffffffffffffffffffffffffffffffffff" \
          "1690602001909190505061037e565b005b341561018a57fe5b610192610484565b6040518080602001828103825283818151815260" \
          "2001915080519060200190808383600083146101e1575b8051825260208311156101e1576020820191506020810190506020830392" \
          "506101bd565b505050905090810190601f16801561020d5780820380516001836020036101000a031916815260200191505b509250" \
          "505060405180910390f35b341561022357fe5b61022b610522565b604051808215151515815260200191505060405180910390f35b" \
          "341561024d57fe5b610255610535565b604051808215151515815260200191505060405180910390f35b60035481565b6000600090" \
          "54906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1633" \
          "73ffffffffffffffffffffffffffffffffffffffff161415156102d25760006000fd5b600260009054906101000a900460ff161515" \
          "156102ef5760006000fd5b6001600260006101000a81548160ff021916908315150217905550806003819055507fb1aaa9f4484acc" \
          "283375c8e495a44766e4026170797dc9280b4ae2ab5632fb71816040518082815260200191505060405180910390a15b5b50565b60" \
          "0060035490505b90565b600060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b6000600090" \
          "54906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1633" \
          "73ffffffffffffffffffffffffffffffffffffffff161415156103db5760006000fd5b600260009054906101000a900460ff161515" \
          "156103f85760006000fd5b80600060006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffff" \
          "ffffffffffffffffffffffffffffffffff1602179055508073ffffffffffffffffffffffffffffffffffffffff167f191a2405c524" \
          "52c381a62f3b7480f9d3e77a76d7737659fc1030aff54b395dd560405180905060405180910390a25b5b50565b6001805460018160" \
          "0116156101000203166002900480601f01602080910402602001604051908101604052809291908181526020018280546001816001" \
          "161561010002031660029004801561051a5780601f106104ef5761010080835404028352916020019161051a565b82019190600052" \
          "6020600020905b8154815290600101906020018083116104fd57829003601f168201915b505050505081565b600260009054906101" \
          "000a900460ff1681565b6000600260009054906101000a900460ff1690505b905600a165627a7a72305820ed3e2c38177c4a88e910" \
          "a15d89c1a7e9b0534395a3d76f02abe2fdc9cd57a9cb0029a165627a7a723058201542f2e1ea92f43165a6f655c469365bdc5bb05e" \
          "075981b919d3b50c7d3468d80029"

token_bytecode = ""
ultimate_oracle_bytecode = ""
event_bytecode = ""
market_bytecode = ""


class TestDaemonExec(TestCase):
    def setUp(self):
        os.environ.update({'TESTRPC_GAS_LIMIT': '10000000000'})
        self.rpc = TestRPCProvider()
        web3_service = Web3Service(self.rpc)
        self.web3 = web3_service.web3
        # Mock web3
        self.daemon = DaemonFactory()
        self.ipfs = Ipfs()

        self.tx_data = {'from': self.web3.eth.accounts[0], 'gas': 100000000}

        # create token
        token_contract_factory = self.web3.eth.contract(ether_token_abi, bytecode=token_bytecode)
        tx_hash = token_contract_factory.deploy()
        self.ether_token_address = self.web3.eth.getTransactionReceipt(tx_hash).get('contractAddress')

        # create oracles
        centralized_contract_factory = self.web3.eth.contract(centralized_oracle_abi, bytecode=centralized_oracle_bytecode)
        tx_hash = centralized_contract_factory.deploy()
        self.centralized_oracle_factory_address = self.web3.eth.getTransactionReceipt(tx_hash).get('contractAddress')
        self.centralized_oracle_factory = self.web3.eth.contract(self.centralized_oracle_factory_address, abi=centralized_oracle_abi)

        ultimate_contract_factory = self.web3.eth.contract(ultimate_oracle_abi, bytecode=ultimate_oracle_bytecode)
        tx_hash = ultimate_contract_factory.deploy()
        self.ultimate_oracle_factory_address = self.web3.eth.getTransactionReceipt(tx_hash).get('contractAddress')
        self.ultimate_oracle_factory = self.web3.eth.contract(self.ultimate_oracle_factory_address, abi=ultimate_oracle_abi)

        # create event contract
        event_contract = self.web3.eth.contract(event_factory_abi, bytecode=event_bytecode)
        tx_hash = event_contract.deploy()
        self.event_factory_address = self.web3.eth.getTransactionReceipt(tx_hash).get('contractAddress')

        self.contracts = [
            {
                'NAME': 'Centralized Oracle Factory',
                'EVENT_ABI': centralized_oracle_abi,
                'EVENT_DATA_RECEIVER': 'eth.event_receiver.CentralizedOracleFactoryReceiver',
                'ADDRESSES': [self.centralized_oracle_factory_address]
            },
            {
                'NAME': 'Ultimate Oracle Factory',
                'EVENT_ABI': ultimate_oracle_abi,
                'EVENT_DATA_RECEIVER': 'eth.event_receiver.UltimateOracleFactoryReceiver',
                'ADDRESSES': [self.ultimate_oracle_factory_address]
            },
            {
                'NAME': 'Event Factory',
                'EVENT_ABI': event_factory_abi,
                'EVENT_DATA_RECEIVER': 'eth.event_receiver.EventFactoryReceiver',
                'ADDRESSES': [self.event_factory_address]
            }
        ]

        self.listener_under_test = EventListener(self.contracts)

    def tearDown(self):
        self.rpc.server.shutdown()
        self.rpc.server.server_close()
        self.rpc = None

    def create_event_description(self):
        # Create event description
        event_description_factory = EventDescriptionFactory()
        categorical_event_description_json = {
            'title': ' '.join(event_description_factory.title),
            'description': ' '.join(event_description_factory.description),
            'resolution_date': event_description_factory.resolution_date.isoformat(),
            'outcomes': ['A', 'B', 'C']
        }
        ipfs_hash = self.ipfs.post(categorical_event_description_json)
        return ipfs_hash

    def test_create_centralized_oracle(self):
        n_oracles = models.CentralizedOracle.objects.all().count()
        self.assertEqual(n_oracles, 0)
        ipfs_hash = self.create_event_description()
        # Create centralized oracle
        tx_hash = self.centralized_oracle_factory.transact(self.tx_data).createCentralizedOracle(ipfs_hash)
        self.assertIsNotNone(tx_hash)
        self.listener_under_test.execute()
        self.assertEqual(len(models.CentralizedOracle.objects.all()), n_oracles+1)

    def test_create_ultimate_oracle(self):
        spread_multiplier = 3
        challenge_period = 200  # 200s
        challenge_amount = 100  # 100 Wei
        front_runner_period = 50  # 50s

        n_oracles = models.UltimateOracle.objects.all().count()
        self.assertEqual(n_oracles, 0)

        # Create centralized oracle
        ipfs_hash = self.create_event_description()
        tx_hash = self.centralized_oracle_factory.transact(self.tx_data).createCentralizedOracle(ipfs_hash)
        self.listener_under_test.execute()
        centralized_oracle = models.CentralizedOracle.objects.get(event_description__ipfs_hash=ipfs_hash)

        # Create ultimate oracle
        tx_hash = self.ultimate_oracle_factory.transact(self.tx_data).createUltimateOracle(
            centralized_oracle.address,
            self.ether_token_address,
            spread_multiplier,
            challenge_period,
            challenge_amount,
            front_runner_period
        )
        self.assertIsNotNone(tx_hash)

        self.listener_under_test.execute()
        self.assertEqual(len(models.UltimateOracle.objects.all()), n_oracles+1)

    def test_create_categorical_event(self):
        n_events = models.CategoricalEvent.objects.all().count()
        self.assertEquals(n_events, 0)
        # Create centralized oracle
        ipfs_hash = self.create_event_description()
        tx_hash = self.centralized_oracle_factory.transact(self.tx_data).createCentralizedOracle(ipfs_hash)
        self.listener_under_test.execute()
        centralized_oracle = models.CentralizedOracle.objects.get(event_description__ipfs_hash=ipfs_hash)
        event_factory = self.web3.eth.contract(self.event_factory_address, abi=event_factory_abi)
        event_factory.transact(self.tx_data).createCategoricalEvent(self.ether_token_address, centralized_oracle.address, 3)
        self.listener_under_test.execute()
        self.assertEquals(models.CategoricalEvent.objects.all().count(), n_events+1)

    def test_create_scalar_event(self):
        n_events = models.ScalarEvent.objects.all().count()
        self.assertEquals(n_events, 0)
        # Create centralized oracle
        ipfs_hash = self.create_event_description()
        tx_hash = self.centralized_oracle_factory.transact(self.tx_data).createCentralizedOracle(ipfs_hash)
        self.listener_under_test.execute()
        centralized_oracle = models.CentralizedOracle.objects.get(event_description__ipfs_hash=ipfs_hash)

        event_factory = self.web3.eth.contract(self.event_factory_address, abi=event_factory_abi)
        event_factory.transact(self.tx_data).createScalarEvent(self.ether_token_address,
                                                   centralized_oracle.address,
                                                   1,
                                                   2)
        self.listener_under_test.execute()
        self.assertEquals(models.ScalarEvent.objects.all().count(), n_events+1)

    def test_create_market(self):
        n_markets = models.Market.objects.all().count()
        self.assertEquals(n_markets, 0)

        # Create centralized oracle
        ipfs_hash = self.create_event_description()
        tx_hash = self.centralized_oracle_factory.transact(self.tx_data).createCentralizedOracle(ipfs_hash)
        self.listener_under_test.execute()
        centralized_oracle = models.CentralizedOracle.objects.get(event_description__ipfs_hash=ipfs_hash)

        event_factory = self.web3.eth.contract(self.event_factory_address, abi=event_factory_abi)
        event_tx = event_factory.transact(self.tx_data).createCategoricalEvent(self.ether_token_address, centralized_oracle.address, 3)
        self.listener_under_test.execute()
        categorical_event_address = self.web3.eth.getTransactionReceipt(tx_hash).get('contractAddress')

        market_contract = self.web3.eth.contract(market_factory_abi, bytecode=market_bytecode)
        tx_hash = market_contract.deploy()
        market_factory_address = self.web3.eth.getTransactionReceipt(tx_hash).get('contractAddress')
        market_factory = self.web3.eth.contract(market_factory_address, abi=market_factory_abi)
        market_tx = market_factory.transact(self.tx_data).createMarket(categorical_event_address, market_factory.address, 0)

        self.listener_under_test.execute()
        self.assertEquals(models.Market.objects.all().count(), n_markets + 1)

    def test_market_buy_event(self):
        pass

    def test_market_sell_event(self):
        pass

    def test_market_short_sell_event(self):
        pass
