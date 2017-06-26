import os
from json import loads
from gnosisdb.utils import SingletonObject


def path_to(file):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), file))


class AbstractLoader(SingletonObject):
    def load(self, file): pass

    def ether_token(self):
        return self.load('EtherToken')

    def standard_market_factory(self):
        return self.load('StandardMarketFactory')

    def standard_market(self):
        return self.load('StandardMarket')

    def centralized_oracle(self):
        return self.load('CentralizedOracle')

    def centralized_oracle_factory(self):
        return self.load('CentralizedOracleFactory')

    def ultimate_oracle(self):
        return self.load('UltimateOracle')

    def ultimate_oracle_factory(self):
        return self.load('UltimateOracleFactory')

    def event_factory(self):
        return self.load('EventFactory')

    def abstract_event(self):
        return self.load('AbstractEvent')

    def outcome_token(self):
        return self.load('OutcomeToken')


class AbiLoader(AbstractLoader):
    def load(self, abi):
        try:
            file = open(path_to('abi/{}.json'.format(abi)), 'r')
            return loads(file.read())
        except:
            return None


class BytecodeLoader(AbstractLoader):
    def load(self, bytecode):
        try:
            return open(path_to('bin/{}.bin'.format(bytecode)), 'r').read()
        except:
            return None
