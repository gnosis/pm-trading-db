from django.utils.module_loading import import_string
from gnosisdb.eth.chainevent import AbstractAddressesGetter
import unittest
import inspect


class TestModuleLoader(unittest.TestCase):

    def setUp(self):
        import gnosisdb

        class AddressesGetter(AbstractAddressesGetter):
            def get_addresses(self):
                return ['0x0', '0x1']

            def __contains__(self, address):
                return address in ['0x0', '0x1']


        class InvalidAddressesGetter(object):
            def get_addresses(self):
                return ['0x0', '0x1']

            def __contains__(self, address):
                return address in ['0x0', '0x1']

        def addresses_getter():
            return ['0x0', '0x1']

        setattr(gnosisdb, AddressesGetter.__name__, AddressesGetter)
        setattr(gnosisdb, InvalidAddressesGetter.__name__, InvalidAddressesGetter)
        setattr(gnosisdb, addresses_getter.__name__, addresses_getter)

        self.class_path = 'gnosisdb.AddressesGetter'
        self.invalid_class_path = 'gnosisdb.InvalidAddressesGetter'
        self.func_path = 'gnosisdb.addresses_getter'

    def test_import(self):
        clazz = import_string(self.class_path)
        func = import_string(self.func_path)

        self.assertTrue(inspect.isclass(clazz))
        self.assertFalse(inspect.isfunction(clazz))
        self.assertTrue(issubclass(clazz, AbstractAddressesGetter))
        self.assertIsNotNone(clazz().get_addresses())

        self.assertTrue(inspect.isfunction(func))
        self.assertFalse(inspect.isclass(func))

    def test_getting_addresses_utils_function(self):
        clazz_addresses = import_string(self.class_path)().get_addresses()
        # invalid_clazz_addresses = addresses_getter(self.invalid_class_path)
        func_addresses = import_string(self.func_path)().get_addresses()

        self.assertEquals(len(clazz_addresses), 2)
        self.assertEquals(len(func_addresses), 2)

        with self.assertRaises(ImportError):
            import_string(self.invalid_class_path)

        invalid_module_path = 'fake_test_path'

        with self.assertRaises(ImportError):
            import_string(invalid_module_path)

        with self.assertRaises(ImportError):
            import_string(2)
