""" Module for mongo db. """

import json
import re

from bson import json_util
from pymongo import MongoClient
from structlog import get_logger

from backend.api import config
from backend.api.data_repository import Caller, DataRepository


class MongoDB(DataRepository):
    """Class for mongo db."""

    MONGODB_CLIENT: MongoClient = None

    def __init__(self) -> None:
        self.MONGODB_CLIENT = MongoClient(config.CONFIG.mongodb_connection_string)

    def load_caller(self, api_key: str) -> Caller:
        """Load caller from data repository."""

        logger = get_logger().bind(api_key=api_key)
        logger.info("Starting load caller")

        database = self.MONGODB_CLIENT.get_default_database()
        caller: Caller = None
        for document in database.caller.find({"api_key": api_key}):
            result = self._clean_document(document)
            if result:
                caller = Caller(**result)

        logger.info("Completed load caller")
        return caller

    def _clean_document(self, document):
        document = json_util.dumps(document)
        document = self._replace_oid(document)
        document = self._replace_date(document)
        return json.loads(document)

    def _replace_oid(self, string):
        while True:
            pattern = re.compile(r'{\s*"\$oid":\s*("[a-z0-9]{1,}")\s*}')
            match = re.search(pattern, string)
            if match:
                string = string.replace(match.group(0), match.group(1))
            else:
                return string

    def _replace_date(self, string):
        while True:
            pattern = re.compile(r'{\s*"\$date":\s*("[TZ0-9-:.]{1,}")\s*}')
            match = re.search(pattern, string)
            if match:
                string = string.replace(match.group(0), match.group(1))
            else:
                return string
