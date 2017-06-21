from gnosisdb.settings.local import *
from gnosisdb.compiled_contracts import AbiLoader
import json

"""
EtherToken references 0x254dffcd3277c0b1660f6d42efbb754edababc2b
Math references 0x5b1869d9a4c187f2eaa108f3062412ecf0526b24
LMSRMarketMaker references 0x9561c133dd8580860b6b7e504bc5aa500f0f06a7
CentralizedOracleFactory references 0xc89ce4735882c9f0f0fe26686c53074e09b0d550
UltimateOracleFactory references 0xd833215cbcc3f914bd1c9ece3ee7bf8b14f841bb
EventFactory references 0xcfeb869f69431e42cdb54a4f4f105c19c080a601
StandardMarketFactory references 0xe982e462b094850f12af94d21d470e21be9d0e9c
"""

GNOSISDB_CONTRACTS = [
    {
        'ADDRESSES': ['0xc89ce4735882c9f0f0fe26686c53074e09b0d550'],
        'ADDRESSES_GETTER': '',
        'EVENT_ABI': AbiLoader().centralized_oracle_factory(),
        'EVENT_DATA_RECEIVER': 'eth.event_receiver.CentralizedOracleFactoryReceiver',
        'NAME': 'centralizedOracleFactory',
        'PUBLISH': True,
    },
    {
        'ADDRESSES': ['0xd833215cbcc3f914bd1c9ece3ee7bf8b14f841bb'],
        'ADDRESSES_GETTER': '',
        'EVENT_ABI': AbiLoader().ultimate_oracle_factory(),
        'EVENT_DATA_RECEIVER': 'eth.event_receiver.UltimateOracleFactoryReceiver',
        'NAME': 'ultimateOracleFactory',
        'PUBLISH': True,
    },
    {
        'ADDRESSES': ['0xcfeb869f69431e42cdb54a4f4f105c19c080a601'],
        'ADDRESSES_GETTER': '',
        'EVENT_ABI': AbiLoader().event_factory(),
        'EVENT_DATA_RECEIVER': 'eth.event_receiver.EventFactoryReceiver',
        'NAME': 'eventFactory',
        'PUBLISH': True,
    },
    {
        'ADDRESSES': ['0xe982e462b094850f12af94d21d470e21be9d0e9c'],
        'ADDRESSES_GETTER': '',
        'EVENT_ABI': AbiLoader().standard_market_factory(),
        'EVENT_DATA_RECEIVER': 'eth.event_receiver.MarketFactoryReceiver',
        'NAME': 'standardMarketFactory',
        'PUBLISH': True,
        'PUBLISH_UNDER': 'marketFactories'
},
    {
        'ADDRESSES': [],
        'ADDRESSES_GETTER': 'eth.address_getters.MarketAddressGetter',
        'EVENT_ABI': AbiLoader().standard_market(),
        'EVENT_DATA_RECEIVER': 'eth.event_receiver.MarketOrderReceiver',
        'NAME': 'Standard Markets Buy/Sell/Short Receiver'
    },
]

ETHEREUM_NODE_HOST= '172.17.0.1'
ETHEREUM_NODE_PORT = 8545
ETHEREUM_NODE_SSL = 0

# IPFS
IPFS_HOST = 'ipfs'
IPFS_PORT = 5001