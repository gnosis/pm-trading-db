from gnosisdb.settings.local import *


# Insert your rpc config here
ETHEREUM_NODE_HOST= '172.17.0.1'
ETHEREUM_NODE_PORT = 8545
ETHEREUM_NODE_SSL = 0


# GnosisDB Contract Addresses
GNOSISDB_CONTRACTS = [
    {
        'ADDRESSES': ['254dffcd3277c0b1660f6d42efbb754edababc2b'],
        'ADDRESSES_GETTER': '',
        'EVENT_ABI': load_json_file(abi_file_path('CentralizedOracleFactory.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.CentralizedOracleFactoryReceiver',
        'NAME': 'centralizedOracleFactory',
        'PUBLISH': True,
    },
    {
        'ADDRESSES': ['c89ce4735882c9f0f0fe26686c53074e09b0d550'],
        'ADDRESSES_GETTER': '',
        'EVENT_ABI': load_json_file(abi_file_path('UltimateOracleFactory.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.UltimateOracleFactoryReceiver',
        'NAME': 'ultimateOracleFactory',
        'PUBLISH': True,
    },
    {
        'ADDRESSES': ['5b1869d9a4c187f2eaa108f3062412ecf0526b24'],
        'ADDRESSES_GETTER': '',
        'EVENT_ABI': load_json_file(abi_file_path('EventFactory.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.EventFactoryReceiver',
        'NAME': 'eventFactory',
        'PUBLISH': True,
    },
    {
        'ADDRESSES': ['9561c133dd8580860b6b7e504bc5aa500f0f06a7'],
        'ADDRESSES_GETTER': '',
        'EVENT_ABI': load_json_file(abi_file_path('StandardMarketFactory.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.MarketFactoryReceiver',
        'NAME': 'standardMarketFactory',
        'PUBLISH': True,
        'PUBLISH_UNDER': 'marketFactories'
    },
    {
        'ADDRESSES': [],
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