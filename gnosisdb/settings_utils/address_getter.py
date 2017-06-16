from abc import ABCMeta, abstractmethod
from django.utils.module_loading import import_string
import inspect


class AbstractAddressesGetter(object):
    """Abstract AddressesGetter class."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_addresses(self): pass

    @abstractmethod
    def contains_address(self, address): pass


def addresses_getter(module_path):
    """Returns the addresses list.

    :param module_path: a dot separated module path
    :return: array of strings
    """
    if isinstance(module_path, str):
        # check str is a module path, load it and retrieve addresses array
        reference = import_string(module_path)
        if inspect.isclass(reference):
            if issubclass(reference, AbstractAddressesGetter):
                return reference()
            else:
                raise ImportError("AddressesGetter class must inherit from %s " % str(AbstractAddressesGetter.__name__))
        elif inspect.isfunction(reference):
            return reference()
        else:
            raise ImportError("%s doesn't look like a module path" % module_path)
    else:
        raise ImportError("%s doesn't look like a module path" % module_path)
