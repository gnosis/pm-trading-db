# -*- coding: utf-8 -*-
from .base import *

SECRET_KEY = 'DEPeWJKeZfFOtgfFzjk5BVn5lixq9vcfad1axbLWpuap1jyIAH'
DEBUG = True

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
INSTALLED_APPS += ['debug_toolbar', ]

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Django Debug Toolbar config
INTERNAL_IPS = ['localhost', '127.0.0.1', '172.17.0.1', '172.18.0.1']


# Everything is a local address from gnosis.js `npm run migrate`
# Run `ganache-cli --gasLimit 40000000 -d -h 0.0.0.0 -i 437894314312`
# ------------------------------------------------------------------------------
# Tournament settings
# ------------------------------------------------------------------------------
TOURNAMENT_TOKEN = '0x0E696947A06550DEf604e82C26fd9E493e576337'
os.environ['TOURNAMENT_TOKEN'] = '0x0E696947A06550DEf604e82C26fd9E493e576337'
LMSR_MARKET_MAKER = '0x9561C133DD8580860B6b7E504bC5Aa500f0f06a7'

# ------------------------------------------------------------------------------
# Token issuance (optional)
# ------------------------------------------------------------------------------
ETHEREUM_DEFAULT_ACCOUNT = '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'
ETHEREUM_DEFAULT_ACCOUNT_PRIVATE_KEY = '4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
TOURNAMENT_TOKEN_ISSUANCE = '200000000000000000000'

# ------------------------------------------------------------------------------
# Local settings
# ------------------------------------------------------------------------------
os.environ['CENTRALIZED_ORACLE_FACTORY'] = '0xCfEB869F69431e42cdB54A4F4f105C19C080A601'
os.environ['EVENT_FACTORY'] = '0x67B5656d60a809915323Bf2C40A8bEF15A152e3e'
os.environ['MARKET_FACTORY'] = '0xe982E462b094850F12AF94d21D470e21bE9D0E9C'
os.environ['UPORT_IDENTITY_MANAGER'] = '0xABBcD5B340C80B5f1C0545C04C987b87310296aE'
os.environ['GENERIC_IDENTITY_MANAGER_ADDRESS'] = '0xA94B7f0465E98609391C623d0560C5720a3f2D33'

from .events.olympia import ETH_EVENTS  # isort:skip
