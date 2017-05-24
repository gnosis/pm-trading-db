# PyCharm fix
from __future__ import absolute_import
from ethereum.utils import sha3
import unittest
import auth


class TestAuth(unittest.TestCase):
    """python -m unittest tests.test_auth"""

    def __init__(self, *args, **kwargs):
        super(TestAuth, self).__init__(*args, **kwargs)

    def test_validator_extension(self):
        request = {
            "data": {"decimals":10,"description":"What will be the Bitcoin price end 2015 according to Bitstamp.net.","resolutionDate":"2015-12-31T24:00:00Z","title":"What will be the Bitcoin price end 2015","unit":"MilliBit"}
        }
        a = auth.Auth()


if __name__ == '__main__':
    unittest.main()
