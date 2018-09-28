from .local import *

env.read_env(str(ROOT_DIR.path('.env_rinkeby')))

IPFS_HOST = env('IPFS_HOST', default='https://ipfs.infura.io')
ETH_FILTER_MAX_BLOCKS = env.int('ETH_FILTER_MAX_BLOCKS', default=1000)
ETHEREUM_MAX_WORKERS = env.int('ETHEREUM_MAX_WORKERS', default=2)

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
