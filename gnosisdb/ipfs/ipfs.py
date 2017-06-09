# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from gnosisdb.utils import singleton
import ipfsapi

@singleton
class Ipfs(object):

    def __init__(self):
        self.api = ipfsapi.connect('https://ipfs.infura.io', 5001)

    def get(self, ipfs_hash):
        """Returns ipfs_hash's json related object
        :param ipfs_hash:
        :return: json object
        :raise AttributeError
        """
        return self.api.get_json(ipfs_hash)

    def post(self, python_object):
        """Creates an ipfs object
        :param python_object
        :return: the ipfs_hash
        """
        ipfs_hash = None
        
        if (isinstance(python_object, dict)):
            ipfs_hash = self.api.add_json(python_object)

        return ipfs_hash

