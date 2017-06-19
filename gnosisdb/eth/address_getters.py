from django.core.exceptions import ObjectDoesNotExist
from settings_utils.address_getter import AbstractAddressesGetter
from relationaldb.models import Contract, Market


class ContractAddressGetter(AbstractAddressesGetter):
    def __init__(self, model=Contract):
        self.model = model

    def get_addresses(self):
        return self.model.objects.all()

    def contains_address(self, address):
        try:
            self.model.objects.get(address=address)
            return True
        except ObjectDoesNotExist:
            return False


class MarketAddressGetter(ContractAddressGetter):
    def __init__(self, model = Market):
        super(MarketAddressGetter, self).__init__(model)
