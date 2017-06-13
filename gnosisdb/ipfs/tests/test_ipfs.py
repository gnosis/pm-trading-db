# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from ipfs.ipfs import Ipfs
from ipfsapi.exceptions import ErrorResponse


class TestIpfs(TestCase):

    def test_ipfs(self):
        json_data = {"name": "giacomo"}
        ipfs = Ipfs()
        # create an ipfs object
        ipfs_hash = ipfs.post(json_data)
        # retrieve ipfs object
        ipfs_json_data = ipfs.get(ipfs_hash)
        self.assertEquals(json_data.get("name"), ipfs_json_data.get("name"))

        with self.assertRaises(ErrorResponse):
            ipfs.get("invalidhash")
