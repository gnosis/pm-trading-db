import os
from json import loads
from gnosisdb.utils import SingletonObject

def path_to(file):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), file))

class AbiLoader(SingletonObject):
    def load(self, abi):
        try:
            file = open(path_to('abi/{}'.format(abi)), 'r')
            return loads(file.read())
        except:
            return None

    def ether_token(self):
        return self.load('EtherToken.json')

    def standard_market_factory(self):
        return self.load('StandardMarketFactory.json')

    def standard_market(self):
        return self.load('StandardMarket.json')

    def centralized_oracle(self):
        return self.load('CentralizedOracle.json')

    def centralized_oracle_factory(self):
        return self.load('CentralizedOracleFactory.json')

    def ultimate_oracle(self):
        return self.load('UltimateOracle.json')

    def ultimate_oracle_factory(self):
        return self.load('UltimateOracleFactory.json')

    def event_factory(self):
        return self.load('EventFactory.json')
