# -*- coding: utf-8 -*-
from ipfsapi import connect
from celery.utils.log import get_task_logger
from django.conf import settings
from json import dumps

from gnosis.utils import singleton


logger = get_task_logger(__name__)

DEFAULT_IPFS_TIMEOUT: int = 120


@singleton
class Ipfs:
    def __init__(self, **kwargs):
        self._defaults = {
            'timeout': settings.IPFS_TIMEOUT,
            **kwargs
        }

        self.api = connect(settings.IPFS_HOST, settings.IPFS_PORT)
        logger.debug('Connection to IPFS (%s : %s) established.' % (settings.IPFS_HOST, settings.IPFS_PORT))

    def get(self, ipfs_hash):
        """Returns ipfs_hash's json related object
        :param ipfs_hash:
        :return: json object
        :raise AttributeError
        """
        logger.debug('Get JSON for IPFS HASH %s' % ipfs_hash)
        json = self.api.get_json(ipfs_hash, **self._defaults)
        logger.debug('Got JSON from IPFS: {}'.format(dumps(json, indent=4)))
        return json

    def post(self, python_object):
        """Creates an ipfs object
        :param python_object
        :return: the ipfs_hash
        """
        ipfs_hash = None

        if (isinstance(python_object, dict)):
            ipfs_hash = self.api.add_json(python_object)

        return ipfs_hash
