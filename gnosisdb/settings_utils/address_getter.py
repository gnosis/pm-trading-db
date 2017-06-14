from abc import ABCMeta, abstractmethod


class AbstractAddressesGetter(object):
    """Abstract AddressesGetter class."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_addresses(self): pass
