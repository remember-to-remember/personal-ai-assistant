""" Module for enumerations. """

from enum import StrEnum, auto


class DataRepositoryType(StrEnum):
    """Class for storing data repository type enumeration."""

    MONGO_DB = auto()


class InferenceProviderType(StrEnum):
    """Class for storing inference provider type enumeration."""

    LLM_LLAMA_INSTRUCT = auto()


class MessagingProviderType(StrEnum):
    """Class for storing messaging provider type enumeration."""

    WHATSAPP_FOR_BUSINESS = auto()
