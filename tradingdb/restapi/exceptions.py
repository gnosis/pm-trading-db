from rest_framework.exceptions import APIException


class InvalidEthereumAddressForFilter(APIException):
    def __init__(self, detail, code=400):
        # Set the response `status_code`, override default 500 error
        self.status_code = code
        super().__init__(detail, code)
