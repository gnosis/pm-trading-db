from bitcoin import ecdsa_recover, ecdsa_raw_recover, encode_pubkey, pubkey_to_address, ecdsa_raw_verify
from ethereum.utils import sha3


class Auth(object):

    def __init__(self):
        pass

    def extract_pubkey(self, msg_hash, v, r, s):
        return encode_pubkey(ecdsa_raw_recover(msg_hash, [v, r, s]), 'hex')

    def pub_to_address(self, pub, hex_format=True):
        """
        Gets an ethereum address from a public key
        :param pub: str - either in hex or bin
        :param hex_format: bool - controls output format.
                                  If set returns a 42 chars hex str prefixed by `0x`.
                                  Otherwise the bin str representation.
        :return: str
        """
        if len(pub) > 32:
            pub = pub.decode('hex')
        address = sha3(pub[1:])[12:]
        return u'0x' + address.encode('hex') if hex_format else address

    def verify_address(self, msg_hash, v, r, s):
        pubkey = self.extract_pubkey(msg_hash, v, r, s)
        return ecdsa_raw_verify(msg_hash, [v,r,s], pubkey)

    def recover_address(self, v, r, s, msg_hash):
        is_valid = self.verify_address(msg_hash, v, r, s)
        if not is_valid:
            return None

        pubkey = self.extract_pubkey(msg_hash, v, r, s)
        address = self.pub_to_address(pubkey, hex_format=True)
        return address

    def recover_address_by_signature(self, signature, msg_hash):
        pubkey = ecdsa_recover(msg_hash, signature)
        address = pubkey_to_address(pubkey)
        return address