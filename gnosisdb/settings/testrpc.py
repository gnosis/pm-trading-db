from gnosisdb.settings.local import *
from gnosisdb.chainevents.abis import abi_file_path, load_json_file

# TestRPC
# insert your rpc config here, ex. localhost - 0.0.0.0 - 192.168.0.1
ETHEREUM_NODE_HOST= 'testrpc'
ETHEREUM_NODE_PORT = 8545
ETHEREUM_NODE_SSL = 0

# IPFS
# You can choose between ipfs container address and 'https://ipfs.infura.io'
IPFS_HOST = 'ipfs'
IPFS_PORT = 5001

# LMSR Market Maker Address
LMSR_MARKET_MAKER = '2f2be9db638cb31d4143cbc1525b0e104f7ed597'

# GnosisDB Contract Addresses
ETH_EVENTS = [
    {
        'ADDRESSES': ['15fdb1d1d083ae5593c7904285ed7f264e10dd3f'],
        'EVENT_ABI': load_json_file(abi_file_path('CentralizedOracleFactory.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.CentralizedOracleFactoryReceiver',
        'NAME': 'centralizedOracleFactory',
        'PUBLISH': True,
    },
    {
        'ADDRESSES': ['d833215cbcc3f914bd1c9ece3ee7bf8b14f841bb'],
        'EVENT_ABI': load_json_file(abi_file_path('UltimateOracleFactory.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.UltimateOracleFactoryReceiver',
        'NAME': 'ultimateOracleFactory',
        'PUBLISH': True,
    },
    {
        'ADDRESSES': ['be2238e8d2bf13188a2a24b41301d7dbda4076be'],
        'EVENT_ABI': load_json_file(abi_file_path('EventFactory.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.EventFactoryReceiver',
        'NAME': 'eventFactory',
        'PUBLISH': True,
    },
    {
        'ADDRESSES': ['371684dfcb1f938c9bdc12bab0856e2cd719f389'],
        'EVENT_ABI': load_json_file(abi_file_path('StandardMarketFactory.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.MarketFactoryReceiver',
        'NAME': 'standardMarketFactory',
        'PUBLISH': True,
        'PUBLISH_UNDER': 'marketFactories'
    },
    {
        'ADDRESSES_GETTER': 'chainevents.address_getters.MarketAddressGetter',
        'EVENT_ABI': load_json_file(abi_file_path('StandardMarket.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.MarketInstanceReceiver',
        'NAME': 'Standard Markets Buy/Sell/Short Receiver'
    },
    {
        'ADDRESSES_GETTER': 'chainevents.address_getters.EventAddressGetter',
        'EVENT_ABI': load_json_file(abi_file_path('AbstractEvent.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.EventInstanceReceiver',
        'NAME': 'Event Instances'
    },
    {
        'ADDRESSES_GETTER': 'chainevents.address_getters.OutcomeTokenGetter',
        'EVENT_ABI': load_json_file(abi_file_path('OutcomeToken.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.OutcomeTokenInstanceReceiver',
        'NAME': 'Outcome Token Instances'
    },
    {
        'ADDRESSES_GETTER': 'chainevents.address_getters.CentralizedOracleGetter',
        'EVENT_ABI': load_json_file(abi_file_path('CentralizedOracle.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.CentralizedOracleInstanceReceiver',
        'NAME': 'Centralized Oracle Instances'
    },
    {
        'ADDRESSES_GETTER': 'chainevents.address_getters.UltimateOracleGetter',
        'EVENT_ABI': load_json_file(abi_file_path('UltimateOracle.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.UltimateOracleInstanceReceiver',
        'NAME': 'Ultimate Oracle Instances'
    },
]
