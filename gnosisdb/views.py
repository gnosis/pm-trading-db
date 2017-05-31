# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework.generics import CreateAPIView
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings
from ethereum.utils import sha3
from gnosisdb.validators.schema_validator import Validator, GnosisValidationError
from gnosisdb.auth.auth import Auth
from utils import limit_content_length
import json


class CreateView(CreateAPIView):

    def __init__(self, *args, **kwargs):
        self.auth = Auth()
        self.validator = getattr(settings, 'GNOSISDB_VALIDATOR')
        super(CreateView, self).__init__(*args, **kwargs)

    @limit_content_length(settings.GNOSISDB_MAX_DOCUMENT_SIZE)
    def post(self, request, *args, **kwargs):

        # check all required main fields
        if 'collection' not in request.data or 'signature' not in request.data \
                or 'data' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={})

        # check signature
        if 'v' not in request.data.get('signature') or 'r' not in request.data.get('signature') \
                or 's' not in request.data.get('signature'):
            return Response(status=status.HTTP_400_BAD_REQUEST, data={})

        v = request.data.get('signature').get('v')
        r = request.data.get('signature').get('r')
        s = request.data.get('signature').get('s')

        msg = json.dumps(request.data.get('data'), separators=(',', ':'))
        # This is old eth_sign implementation
        # TODO use personal sign
        msg_hash = sha3(msg).encode('hex')
        try:
            address = self.auth.recover_address(v, r, s, msg_hash)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={})

        # check if collection in available collections - retrieve info from config
        # schema = GnosisDB.get_schema_file_name(json_data.get('collection'))
        try:
            self.validator.set_schema(request.data.get('collection'))
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={})

        try:
            self.validator.validate(request.data.get('data'))
        except GnosisValidationError as ve:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={})

        # TODO write data

        return Response(status=status.HTTP_200_OK, data={})

