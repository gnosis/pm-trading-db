from mpmath import mp, mpf


def singleton(clazz):
    instances = {}
    def getinstance(*args, **kwargs):
        if clazz not in instances:
            instances[clazz] = clazz(*args, **kwargs)
        return instances[clazz]
    return getinstance


class SingletonObject(object):
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls._instances.get(cls, None) is None:
            cls._instances[cls] = super(SingletonObject, cls).__new__(cls, *args, **kwargs)
        return SingletonObject._instances[cls]


def remove_null_values(obj):
    """
    Remove all null values from a dictionary
    :param obj: dictionary
    :return: filtered dictionary
    """
    if not isinstance(obj, dict):
        return obj

    keys = obj.keys()
    for k in keys:
        _obj = obj[k]
        if _obj is None:
            del obj[k]
        elif isinstance(obj[k], dict):
            remove_null_values(obj[k])

    return obj


def add_0x_prefix(value):
    return '0x' + value if value[:2] not in (b'0x', '0x') else value


def calc_lmsr_marginal_price(token_index, net_outcome_tokens_sold, funding):
    b = mpf(funding) / mp.log(len(net_outcome_tokens_sold))
    return float(mp.exp(net_outcome_tokens_sold[token_index]/b) / sum(mp.exp(share_count/b) for share_count in net_outcome_tokens_sold))
