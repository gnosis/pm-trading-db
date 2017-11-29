from relationaldb.models import Contract, Market, Event, OutcomeToken, CentralizedOracle
from django.core.exceptions import ObjectDoesNotExist
from django_eth_events.chainevents import AbstractAddressesGetter


class ContractAddressGetter(AbstractAddressesGetter):
    """
    Returns the addresses used by event listener in order to filter logs triggered by Contract Instances
    """
    class Meta:
        model = Contract

    def get_addresses(self):
        """
        Returns list of ethereum addresses
        :return: [address]
        """
        return list(self.Meta.model.objects.values_list('address', flat=True))

    def __contains__(self, address):
        """
        Checks if address is contained on the Contract collection
        :param address: ethereum address string
        :return: Boolean
        """
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


class OutcomeTokenGetter(ContractAddressGetter):
    class Meta:
        model = OutcomeToken


class CentralizedOracleGetter(ContractAddressGetter):
    class Meta:
        model = CentralizedOracle
