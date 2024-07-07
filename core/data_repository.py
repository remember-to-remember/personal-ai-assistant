""" Module for data repository. """

from abc import ABC, abstractmethod

from pydantic.dataclasses import dataclass


@dataclass
class Caller:
    """Class for caller collection."""

    # core fields
    _id: str
    api_key: str
    name: str


class DataRepository(ABC):
    """Class for data repository."""

    @abstractmethod
    def load_caller(self, api_key: str) -> Caller:
        """Load caller from data repository."""
