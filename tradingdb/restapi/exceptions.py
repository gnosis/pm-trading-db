from rest_framework.exceptions import APIException, status


class InvalidEthereumAddressForFilter(APIException):
    def __init__(self, detail, code=400):
        self.status_code = status.HTTP_400_BAD_REQUEST
        super().__init__(detail, code)
