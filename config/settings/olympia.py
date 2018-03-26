from gnosisdb.chainevents.abis import abi_file_path, load_json_file

from .base import *

# OLYMPIA
LMSR_MARKET_MAKER = '0x9561C133DD8580860B6b7E504bC5Aa500f0f06a7'
ETHEREUM_DEFAULT_ACCOUNT = '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'
TOURNAMENT_TOKEN = '0x254dffcd3277C0b1660F6d42EFbB754edaBAbC2B'
TOURNAMENT_TOKEN_ISSUANCE = '200000000000000000000'

# ------------------------------------------------------------------------------
# GnosisDB Contract Addresses (Rinkeby)
# ------------------------------------------------------------------------------
ETH_EVENTS = [
    {
        'ADDRESSES': ['0xb3289eAAc0Fe3eD15Df177F925c6F8ceEB908b8f'],
        'EVENT_ABI': load_json_file(abi_file_path('CentralizedOracleFactory.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.CentralizedOracleFactoryReceiver',
        'NAME': 'centralizedOracleFactory',
        'PUBLISH': True,
    },
    {
        'ADDRESSES': ['0x0f60faf69F3Ac146e1E557247583BC0c84f9f086'],
        'EVENT_ABI': load_json_file(abi_file_path('EventFactory.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.EventFactoryReceiver',
        'NAME': 'eventFactory',
        'PUBLISH': True,
    },
    {
        'ADDRESSES': ['0xEAA325bACAe405fd5B45E9cF695D391F1C624A2f'],
        'EVENT_ABI': load_json_file(abi_file_path('StandardMarketFactory.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.MarketFactoryReceiver',
        'NAME': 'standardMarketFactory',
        'PUBLISH': True,
        'PUBLISH_UNDER': 'marketFactories'
    },
    {
        'ADDRESSES': ['0xABBcD5B340C80B5f1C0545C04C987b87310296aE'],
        'EVENT_ABI': load_json_file(abi_file_path('UportIdentityManager.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.UportIdentityManagerReceiver',
        'NAME': 'UportIdentityManagerInstanceReceiver',
        'PUBLISH': True,
    },
    {
        'ADDRESSES': ['0x79DA1C9eF6bf6bC64E66F8AbFFDDC1A093E50f13'],
        'EVENT_ABI': load_json_file(abi_file_path('AddressRegistry.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.GenericIdentityManagerReceiver',
        'NAME': 'GenericIdentityManagerReceiver',
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
]
