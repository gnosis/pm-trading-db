from .base import *


# Everything is a local address from gnosis.js `npm run migrate --network quickstart`
# Run `ganache-cli --gasLimit 40000000 -d -h 0.0.0.0 -i 437894314312`

env.read_env(str(ROOT_DIR.path('.env_local')))


SECRET_KEY = 'DEPeWJKeZfFOtgfFzjk5BVn5lixq9vcfad1axbLWpuap1jyIAH'
DEBUG = True

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
INSTALLED_APPS += ['debug_toolbar', ]

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Django Debug Toolbar config
INTERNAL_IPS = ['localhost', '127.0.0.1', '172.17.0.1', '172.18.0.1']

# ------------------------------------------------------------------------------
# IPFS
# ------------------------------------------------------------------------------
IPFS_HOST = env('IPFS_HOST', default=IPFS_HOST) # use IPFS_HOST from .env_local if provided, otherwise base.IPFS_HOST

# ------------------------------------------------------------------------------
# Tournament settings
# ------------------------------------------------------------------------------
TOURNAMENT_TOKEN = env('TOURNAMENT_TOKEN')
LMSR_MARKET_MAKER = env('LMSR_MARKET_MAKER')

# ------------------------------------------------------------------------------
# Token issuance (optional)
# ------------------------------------------------------------------------------
ETHEREUM_DEFAULT_ACCOUNT = env('ETHEREUM_DEFAULT_ACCOUNT', default=None)
ETHEREUM_DEFAULT_ACCOUNT_PRIVATE_KEY = env('ETHEREUM_DEFAULT_ACCOUNT_PRIVATE_KEY', default=None)
TOURNAMENT_TOKEN_ISSUANCE = env.int('TOURNAMENT_TOKEN_ISSUANCE', 200000000000000000000)
ISSUANCE_GAS = env.int('ISSUANCE_GAS', 2000000)
ISSUANCE_GAS_PRICE = env.int('ISSUANCE_GAS_PRICE', 50000000000)

from .events.olympia import ETH_EVENTS  # isort:skip