from .base import *

SECRET_KEY = 'DEPeWJKeZfFOtgfFzjk5BVn5lixq9vcfad1axbLWpuap1jyIAH'
DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# ------------------------------------------------------------------------------
# Ethereum node
# ------------------------------------------------------------------------------
ETHEREUM_NODE_HOST = '172.17.0.1'
ETHEREUM_NODE_PORT = 8545
ETHEREUM_NODE_SSL = 0

ETH_PROCESS_BLOCKS = 100

# ------------------------------------------------------------------------------
# Tournament settings
# ------------------------------------------------------------------------------
TOURNAMENT_TOKEN = '0xa0c107Db0e9194c18359d3265289239453b56CF2'
os.environ['TOURNAMENT_TOKEN'] = TOURNAMENT_TOKEN
LMSR_MARKET_MAKER = '0x11B5257396f156027B9232da7220bd7447282DB6'

# ------------------------------------------------------------------------------
# Token issuance (optional)
# ------------------------------------------------------------------------------
ETHEREUM_DEFAULT_ACCOUNT = '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'
ETHEREUM_DEFAULT_ACCOUNT_PRIVATE_KEY = '4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
TOURNAMENT_TOKEN_ISSUANCE = '200000000000000000000'
ISSUANCE_GAS = 2000000
ISSUANCE_GAS_PRICE = 50000000000

# ------------------------------------------------------------------------------
# Local settings
# ------------------------------------------------------------------------------
os.environ['CENTRALIZED_ORACLE_FACTORY'] = '0xb3289eAAc0Fe3eD15Df177F925c6F8ceEB908b8f'
os.environ['EVENT_FACTORY'] = '0x0f60faf69F3Ac146e1E557247583BC0c84f9f086'
os.environ['MARKET_FACTORY'] = '0xEAA325bACAe405fd5B45E9cF695D391F1C624A2f'
os.environ['UPORT_IDENTITY_MANAGER'] = '0xABBcD5B340C80B5f1C0545C04C987b87310296aE'
os.environ['GENERIC_IDENTITY_MANAGER_ADDRESS'] = '0x79DA1C9eF6bf6bC64E66F8AbFFDDC1A093E50f13'

from .events.olympia import ETH_EVENTS  # isort:skip
