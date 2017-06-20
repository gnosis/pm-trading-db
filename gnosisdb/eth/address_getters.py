from django.core.exceptions import ObjectDoesNotExist
from settings_utils.address_getter import AbstractAddressesGetter
from relationaldb.models import Contract, Market, Event


class ContractAddressGetter(AbstractAddressesGetter):
    class Meta:
        model = Contract

    def get_addresses(self):
        return list(self.Meta.model.objects.values_list('address', flat=True))

    def __contains__(self, address):
        try:
            self.Meta.model.objects.get(address=address)
            return True
        except ObjectDoesNotExist:
            return False


class MarketAddressGetter(ContractAddressGetter):
    class Meta:
        model = Market


class EventAddressGetter(ContractAddressGetter):
    class Meta:
        model = Event
