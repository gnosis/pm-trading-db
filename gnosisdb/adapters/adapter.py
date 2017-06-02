from __future__ import absolute_import
from abc import abstractmethod, ABCMeta


class SingletonABCMeta(ABCMeta):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonABCMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Adapter:
    __metaclass__ = SingletonABCMeta

    def __init__(self, config):
        """
        :param config:
        """
        self.config = config
        self.client = None

    @abstractmethod
    def connect(self):
        """
        Initializes the adapter connection pool
        :return: Connection
        """

    @abstractmethod
    def disconnect(self):
        """
        Closes the database connection
        :return: Boolean
        """

    @abstractmethod
    def write(self, collection, schema, data):
        """
        Inserts on the database collection the given data
        following the schema
        :param collection: String
        :param schema: Dictionary
        :param data: Dictionary
        :return: Boolean
        """
