from .local import *

env.read_env(str(ROOT_DIR.path('.env_rinkeby')))

IPFS_HOST = 'https://ipfs.infura.io'

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
