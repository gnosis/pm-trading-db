from gnosisdb.settings.local import *
import json

GNOSISDB_CONTRACTS = [
    {
        'ADDRESSES': ['0xca3f881ff5b6e0c388cd9717aa5127a089fb1363'],
        'ADDRESSES_GETTER': '',
        'EVENT_ABI': json.loads('[{"inputs": [{"type": "bytes", "name": "ipfsHash"}], "constant": false, "name": "createCentralizedOracle", "payable": false, "outputs": [{"type": "address", "name": "centralizedOracle"}], "type": "function"}, {"inputs": [{"indexed": true, "type": "address", "name": "creator"}, {"indexed": false, "type": "address", "name": "centralizedOracle"}, {"indexed": false, "type": "bytes", "name": "ipfsHash"}], "type": "event", "name": "CentralizedOracleCreation", "anonymous": false}]'),
        'EVENT_DATA_RECEIVER': 'eth.event_receiver.CentralizedOracleReceiver',
        'NAME': 'Centralized Oracle Factory' # optional
    },
    {
        'ADDRESSES': ['0x7506a6f972ba15fdeee0a7820822dc57daf5a494'],
        'ADDRESSES_GETTER': '',
        'EVENT_ABI': json.loads('[{"inputs": [{"type": "address", "name": "collateralToken"}, {"type": "address", "name": "oracle"}, {"type": "int256", "name": "lowerBound"}, {"type": "int256", "name": "upperBound"}], "constant": false, "name": "createScalarEvent", "payable": false, "outputs": [{"type": "address", "name": "eventContract"}], "type": "function"}, {"inputs": [{"type": "bytes32", "name": ""}], "constant": true, "name": "categoricalEvents", "payable": false, "outputs": [{"type": "address", "name": ""}], "type": "function"}, {"inputs": [{"type": "bytes32", "name": ""}], "constant": true, "name": "scalarEvents", "payable": false, "outputs": [{"type": "address", "name": ""}], "type": "function"}, {"inputs": [{"type": "address", "name": "collateralToken"}, {"type": "address", "name": "oracle"}, {"type": "uint8", "name": "outcomeCount"}], "constant": false, "name": "createCategoricalEvent", "payable": false, "outputs": [{"type": "address", "name": "eventContract"}], "type": "function"}, {"inputs": [{"indexed": true, "type": "address", "name": "creator"}, {"indexed": false, "type": "address", "name": "categoricalEvent"}, {"indexed": false, "type": "address", "name": "collateralToken"}, {"indexed": false, "type": "address", "name": "oracle"}, {"indexed": false, "type": "uint8", "name": "outcomeCount"}], "type": "event", "name": "CategoricalEventCreation", "anonymous": false}, {"inputs": [{"indexed": true, "type": "address", "name": "creator"}, {"indexed": false, "type": "address", "name": "scalarEvent"}, {"indexed": false, "type": "address", "name": "collateralToken"}, {"indexed": false, "type": "address", "name": "oracle"}, {"indexed": false, "type": "int256", "name": "lowerBound"}, {"indexed": false, "type": "int256", "name": "upperBound"}], "type": "event", "name": "ScalarEventCreation", "anonymous": false}]'),
        'EVENT_DATA_RECEIVER': 'eth.event_receiver.EventReceiver',
        'NAME': 'Event Factory'
    },
    {
        'ADDRESSES': ['0x2f2be9db638cb31d4143cbc1525b0e104f7ed597'],
        'ADDRESSES_GETTER': '',
        'EVENT_ABI': json.loads('[{"inputs": [{"type": "address", "name": "eventContract"}, {"type": "address", "name": "marketMaker"}, {"type": "uint24", "name": "fee"}], "constant": false, "name": "createMarket", "payable": false, "outputs": [{"type": "address", "name": "market"}], "type": "function"}, {"inputs": [{"indexed": true, "type": "address", "name": "creator"}, {"indexed": false, "type": "address", "name": "market"}, {"indexed": false, "type": "address", "name": "eventContract"}, {"indexed": false, "type": "address", "name": "marketMaker"}, {"indexed": false, "type": "uint24", "name": "fee"}], "type": "event", "name": "MarketCreation", "anonymous": false}]'),
        'EVENT_DATA_RECEIVER': 'eth.event_receiver.MarketReceiver',
        'NAME': 'Standard Market Factory'
    },
    {
        'ADDRESSES': ['0x9f04e7d93e0bbe5f3b22a9738e9b6c18dc6762dc'],
        'ADDRESSES_GETTER': '',
        'EVENT_ABI': json.loads('[{"inputs": [{"type": "address", "name": "oracle"}, {"type": "address", "name": "collateralToken"}, {"type": "uint8", "name": "spreadMultiplier"}, {"type": "uint256", "name": "challengePeriod"}, {"type": "uint256", "name": "challengeAmount"}, {"type": "uint256", "name": "frontRunnerPeriod"}], "constant": false, "name": "createUltimateOracle", "payable": false, "outputs": [{"type": "address", "name": "ultimateOracle"}], "type": "function"}, {"inputs": [{"indexed": true, "type": "address", "name": "creator"}, {"indexed": false, "type": "address", "name": "ultimateOracle"}, {"indexed": false, "type": "address", "name": "oracle"}, {"indexed": false, "type": "address", "name": "collateralToken"}, {"indexed": false, "type": "uint8", "name": "spreadMultiplier"}, {"indexed": false, "type": "uint256", "name": "challengePeriod"}, {"indexed": false, "type": "uint256", "name": "challengeAmount"}, {"indexed": false, "type": "uint256", "name": "frontRunnerPeriod"}], "type": "event", "name": "UltimateOracleCreation", "anonymous": false}]'),
        'EVENT_DATA_RECEIVER': 'eth.event_receiver.UltimateOracleReceiver',
        'NAME': 'Ultimate Oracle Factory'
    }
]

ETHEREUM_NODE_HOST= '192.168.1.165'
ETHEREUM_NODE_PORT = 8545
ETHEREUM_NODE_SSL = 0

# IPFS
IPFS_HOST = 'ipfs'
IPFS_PORT = 5001
