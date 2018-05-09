import os

from tradingdb.chainevents.abis import abi_file_path, load_json_file

from .base import ETH_EVENTS

OLYMPIA_EVENTS = [
    {
        'ADDRESSES': [os.environ['UPORT_IDENTITY_MANAGER']],
        'EVENT_ABI': load_json_file(abi_file_path('UportIdentityManager.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.UportIdentityManagerReceiver',
        'NAME': 'UportIdentityManagerInstanceReceiver',
        'PUBLISH': True,
    },
    {
        'ADDRESSES': [os.environ['GENERIC_IDENTITY_MANAGER_ADDRESS']],
        'EVENT_ABI': load_json_file(abi_file_path('AddressRegistry.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.GenericIdentityManagerReceiver',
        'NAME': 'GenericIdentityManagerReceiver',
        'PUBLISH': True,
    },
    {
        'ADDRESSES': [os.environ['TOURNAMENT_TOKEN']],
        'EVENT_ABI': load_json_file(abi_file_path('TournamentToken.json')),
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.TournamentTokenReceiver',
        'NAME': 'OlympiaToken',
        'PUBLISH': True,
    },
]

ETH_EVENTS = ETH_EVENTS[:3] + OLYMPIA_EVENTS + ETH_EVENTS[3:]
