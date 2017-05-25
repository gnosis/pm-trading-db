from __future__ import absolute_import
from bitcoin import ecdsa_raw_sign, privtopub
from ethereum.utils import sha3
from auth import Auth
import unittest
import json


class TestAuth(unittest.TestCase):

    def setUp(self):
        self.privkey = sha3(b'safe very safe').encode('hex')
        self.pubkey = privtopub(self.privkey)
        self.message = {
            'a string': 'hey ho',
            'a number': 1,
            'a list': ['a', 0],
        }
        self.json_message = json.dumps(self.message, separators=(',', ':'))
        self.msg_hash = sha3(self.json_message).encode('hex')
        self.v, self.r, self.s = ecdsa_raw_sign(self.msg_hash, self.privkey)

    def test_signing(self):
        auth = Auth()
        address = auth.recover_address(self.v, self.r, self.s, self.msg_hash)
        self.assertIsNotNone(address)
        self.assertEquals(42, len(address))

        # create an other private key
        self.other_privkey = sha3(b'other safe very safe').encode('hex')
        self.other_pubkey = privtopub(self.other_privkey)

        self.assertNotEquals(self.privkey, self.other_privkey)