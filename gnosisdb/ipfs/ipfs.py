# -*- coding: utf-8 -*-
import ipfsapi
from django.conf import settings

from utils import singleton


@singleton
class Ipfs(object):

    def __init__(self):
        self.api = ipfsapi.connect(settings.IPFS_HOST, settings.IPFS_PORT)

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
