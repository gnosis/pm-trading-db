# -*- coding: utf-8 -*-
from django.test import TestCase
from ipfsapi.exceptions import ErrorResponse

from ..ipfs import Ipfs


class TestIpfs(TestCase):

    def test_ipfs(self):
        json_data = {"name": "giacomo", "another_name": "uxío"}
        ipfs = Ipfs()
        # create an ipfs object
        ipfs_hash = ipfs.post(json_data)
        # retrieve ipfs object
        ipfs_json_data = ipfs.get(ipfs_hash)
        self.assertDictEqual(json_data, ipfs_json_data)

        with self.assertRaises(ErrorResponse):
            ipfs.get("invalidhash")
