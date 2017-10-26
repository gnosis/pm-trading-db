from gnosisdb.settings.testrpc import *
from gnosisdb.chainevents.abis import abi_file_path, load_json_file
ETHEREUM_NODE_HOST= '10.1.0.14'
TOURNAMENT_TOKEN = '254dffcd3277c0b1660f6d42efbb754edababc2b'
ETHEREUM_PRIVATE_KEY = '4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'

# ------------------------------------------------------------------------------
# GNOSIS ETHEREUM CONTRACTS
# ------------------------------------------------------------------------------

ETH_EVENTS = [
    {
        'ADDRESSES': ['b3289eaac0fe3ed15df177f925c6f8ceeb908b8f'],
        'EVENT_ABI': load_json_file(abi_file_path('CentralizedOracleFactory.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.CentralizedOracleFactoryReceiver',
        'NAME': 'centralizedOracleFactory',
        'PUBLISH': True,
    },
    {
        'ADDRESSES': ['0f60faf69f3ac146e1e557247583bc0c84f9f086'],
        'EVENT_ABI': load_json_file(abi_file_path('EventFactory.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.EventFactoryReceiver',
        'NAME': 'eventFactory',
        'PUBLISH': True,
    },
    {
        'ADDRESSES': ['eaa325bacae405fd5b45e9cf695d391f1c624a2f'],
        'EVENT_ABI': load_json_file(abi_file_path('StandardMarketFactory.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.MarketFactoryReceiver',
        'NAME': 'standardMarketFactory',
        'PUBLISH': True,
        'PUBLISH_UNDER': 'marketFactories'
    },
    {
        'ADDRESSES': ['abbcd5b340c80b5f1c0545c04c987b87310296ae'],
        'EVENT_ABI': load_json_file(abi_file_path('UportIdentityManager.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.UportIdentityManagerReceiver',
        'NAME': 'UportIdentityManagerInstanceReceiver',
        'PUBLISH': True,
    },
    {
        'ADDRESSES': [TOURNAMENT_TOKEN],
        'EVENT_ABI': load_json_file(abi_file_path('TournamentToken.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.TournamentTokenReceiver',
        'NAME': 'OlympiaToken',
        'PUBLISH': True,
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
