from gnosisdb.settings.local import *
import json

"""
EtherToken references 0xcfeb869f69431e42cdb54a4f4f105c19c080a601
Math references 0xe78a0f7e598cc8b0bb87894b0f60dd2a88d6a8ab
LMSRMarketMaker references 0xd833215cbcc3f914bd1c9ece3ee7bf8b14f841bb
CentralizedOracleFactory references 0x254dffcd3277c0b1660f6d42efbb754edababc2b
UltimateOracleFactory references 0xc89ce4735882c9f0f0fe26686c53074e09b0d550
EventFactory references 0x5b1869d9a4c187f2eaa108f3062412ecf0526b24
StandardMarketFactory references 0x9561c133dd8580860b6b7e504bc5aa500f0f06a7
"""

GNOSISDB_CONTRACTS = [
    {
        'ADDRESSES': ['0x254dffcd3277c0b1660f6d42efbb754edababc2b'],
        'ADDRESSES_GETTER': '',
        'EVENT_ABI': json.loads('[{"inputs": [{"type": "bytes", "name": "ipfsHash"}], "constant": false, "name": "createCentralizedOracle", "payable": false, "outputs": [{"type": "address", "name": "centralizedOracle"}], "type": "function"}, {"inputs": [{"indexed": true, "type": "address", "name": "creator"}, {"indexed": false, "type": "address", "name": "centralizedOracle"}, {"indexed": false, "type": "bytes", "name": "ipfsHash"}], "type": "event", "name": "CentralizedOracleCreation", "anonymous": false}]'),
        'EVENT_DATA_RECEIVER': 'eth.event_receiver.CentralizedOracleReceiver',
        'NAME': 'Centralized Oracle Factory' # optional
    },
    {
        'ADDRESSES': ['0xc89ce4735882c9f0f0fe26686c53074e09b0d550'],
        'ADDRESSES_GETTER': '',
        'EVENT_ABI': json.loads('[{"inputs": [{"type": "address", "name": "oracle"}, {"type": "address", "name": "collateralToken"}, {"type": "uint8", "name": "spreadMultiplier"}, {"type": "uint256", "name": "challengePeriod"}, {"type": "uint256", "name": "challengeAmount"}, {"type": "uint256", "name": "frontRunnerPeriod"}], "constant": false, "name": "createUltimateOracle", "payable": false, "outputs": [{"type": "address", "name": "ultimateOracle"}], "type": "function"}, {"inputs": [{"indexed": true, "type": "address", "name": "creator"}, {"indexed": false, "type": "address", "name": "ultimateOracle"}, {"indexed": false, "type": "address", "name": "oracle"}, {"indexed": false, "type": "address", "name": "collateralToken"}, {"indexed": false, "type": "uint8", "name": "spreadMultiplier"}, {"indexed": false, "type": "uint256", "name": "challengePeriod"}, {"indexed": false, "type": "uint256", "name": "challengeAmount"}, {"indexed": false, "type": "uint256", "name": "frontRunnerPeriod"}], "type": "event", "name": "UltimateOracleCreation", "anonymous": false}]'),
        'EVENT_DATA_RECEIVER': 'eth.event_receiver.UltimateOracleReceiver',
        'NAME': 'Ultimate Oracle Factory'
    },
    {
        'ADDRESSES': ['0x5b1869d9a4c187f2eaa108f3062412ecf0526b24'],
        'ADDRESSES_GETTER': '',
        'EVENT_ABI': json.loads('[{"inputs": [{"type": "address", "name": "collateralToken"}, {"type": "address", "name": "oracle"}, {"type": "int256", "name": "lowerBound"}, {"type": "int256", "name": "upperBound"}], "constant": false, "name": "createScalarEvent", "payable": false, "outputs": [{"type": "address", "name": "eventContract"}], "type": "function"}, {"inputs": [{"type": "bytes32", "name": ""}], "constant": true, "name": "categoricalEvents", "payable": false, "outputs": [{"type": "address", "name": ""}], "type": "function"}, {"inputs": [{"type": "bytes32", "name": ""}], "constant": true, "name": "scalarEvents", "payable": false, "outputs": [{"type": "address", "name": ""}], "type": "function"}, {"inputs": [{"type": "address", "name": "collateralToken"}, {"type": "address", "name": "oracle"}, {"type": "uint8", "name": "outcomeCount"}], "constant": false, "name": "createCategoricalEvent", "payable": false, "outputs": [{"type": "address", "name": "eventContract"}], "type": "function"}, {"inputs": [{"indexed": true, "type": "address", "name": "creator"}, {"indexed": false, "type": "address", "name": "categoricalEvent"}, {"indexed": false, "type": "address", "name": "collateralToken"}, {"indexed": false, "type": "address", "name": "oracle"}, {"indexed": false, "type": "uint8", "name": "outcomeCount"}], "type": "event", "name": "CategoricalEventCreation", "anonymous": false}, {"inputs": [{"indexed": true, "type": "address", "name": "creator"}, {"indexed": false, "type": "address", "name": "scalarEvent"}, {"indexed": false, "type": "address", "name": "collateralToken"}, {"indexed": false, "type": "address", "name": "oracle"}, {"indexed": false, "type": "int256", "name": "lowerBound"}, {"indexed": false, "type": "int256", "name": "upperBound"}], "type": "event", "name": "ScalarEventCreation", "anonymous": false}]'),
        'EVENT_DATA_RECEIVER': 'eth.event_receiver.EventReceiver',
        'NAME': 'Event Factory'
    },
    {
        'ADDRESSES': ['0x9561c133dd8580860b6b7e504bc5aa500f0f06a7'],
        'ADDRESSES_GETTER': '',
        'EVENT_ABI': json.loads('[{"inputs": [{"type": "address", "name": "eventContract"}, {"type": "address", "name": "marketMaker"}, {"type": "uint24", "name": "fee"}], "constant": false, "name": "createMarket", "payable": false, "outputs": [{"type": "address", "name": "market"}], "type": "function"}, {"inputs": [{"indexed": true, "type": "address", "name": "creator"}, {"indexed": false, "type": "address", "name": "market"}, {"indexed": false, "type": "address", "name": "eventContract"}, {"indexed": false, "type": "address", "name": "marketMaker"}, {"indexed": false, "type": "uint24", "name": "fee"}], "type": "event", "name": "MarketCreation", "anonymous": false}]'),
        'EVENT_DATA_RECEIVER': 'eth.event_receiver.MarketReceiver',
        'NAME': 'Standard Market Factory'
    },
]

ETHEREUM_NODE_HOST= 'localhost'
ETHEREUM_NODE_PORT = 8545
ETHEREUM_NODE_SSL = 0

# IPFS
IPFS_HOST = 'ipfs'
IPFS_PORT = 5001
