from typing import Tuple, Union

from django_eth_events.utils import remove_0x_head
from eth_account import Account
from eth_utils import to_normalized_address
from mpmath import mp, mpf


def add_0x_prefix(value):
    return '0x' + value if value[:2] not in (b'0x', '0x') else value


def generate_eth_account(only_address: bool = False, checksum_address: bool = False) -> Union[Tuple[str, str, str], str]:
    account = Account.create()
    if checksum_address:
        # Address is already checksumed, just remove 0x prefix
        address = remove_0x_head(account.address)
    else:
        address = remove_0x_head(to_normalized_address(account.address))

    if only_address:
        return address
    return account.privateKey.hex(), address


def generate_transaction_hash(gas: int = 1000000, gas_price: int = 1000000000, value: int = 0, nonce: int = 0,
                              chain_id: int = 0) -> str:
    (private_key, sender) = generate_eth_account()
    recipient = generate_eth_account(only_address=True, checksum_address=True)

    transaction = {
        'to': '0x%s' % recipient,
        'value': value,
        'gas': gas,
        'gasPrice': gas_price,
        'nonce': nonce,
        'chainId': chain_id
    }

    signature = Account.signTransaction(transaction, private_key)
    return remove_0x_head(signature.get('hash'))


def remove_null_values(obj):
    """
    Remove all null values from a dictionary
    :param obj: dictionary
    :return: filtered dictionary
    """
    if not isinstance(obj, dict):
        return obj

    for k in list(obj.keys()):
        _obj = obj[k]
        if _obj is None:
            del obj[k]
        elif isinstance(obj[k], dict):
            remove_null_values(obj[k])

    return obj


def singleton(clazz):
    instances = {}

    def getinstance(*args, **kwargs):
        if clazz not in instances:
            instances[clazz] = clazz(*args, **kwargs)
        return instances[clazz]
    return getinstance


class SingletonObject:
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls._instances.get(cls, None) is None:
            cls._instances[cls] = super().__new__(cls, *args, **kwargs)
        return SingletonObject._instances[cls]


# =======================================
#       SPECIFIC TO TRADINGDB
# =======================================


def calc_lmsr_marginal_price(token_index, net_outcome_tokens_sold, funding):
    b = mpf(funding) / mp.log(len(net_outcome_tokens_sold))
    return float(mp.exp(net_outcome_tokens_sold[token_index] / b) / sum(mp.exp(share_count / b)
                 for share_count in net_outcome_tokens_sold))


def get_order_type(order):
    """
    Returns the order type (Sell, Short Sell, Buy)
    :param order: See models.Order
    :return: String
    """
    if hasattr(order, 'sellorder'):
        return 'SELL'
    elif hasattr(order, 'shortsellorder'):
        return 'SHORT SELL'
    elif hasattr(order, 'buyorder'):
        return 'BUY'
    else:
        return 'UNKNOWN'


def get_order_cost(order):
    order_type = get_order_type(order)
    if order_type == 'BUY':
        return order.buyorder.cost
    elif order_type == 'SHORT SELL':
        return order.shortsellorder.cost
    else:
        return None


def get_order_profit(order):
    order_type = get_order_type(order)
    if order_type == 'SELL':
        return order.sellorder.profit
    else:
        return None
