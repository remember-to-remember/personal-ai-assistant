""" Module for enumerations. """

from enum import StrEnum, auto


class DataRepositoryType(StrEnum):
    """Class for storing data repository type enumeration."""

    SQLITE = auto()
    MONGO_DB = auto()


class InferenceProviderType(StrEnum):
    """Class for storing inference provider type enumeration."""

    IN_PROCESS = auto()


class MessagingProviderType(StrEnum):
    """Class for storing messaging provider type enumeration."""

    WHATSAPP_FOR_BUSINESS = auto()


class AttachmentType(StrEnum):
    """Class for storing input/response related file type."""

    TEXT_FILE = auto()
    PDF_FILE = auto()
    AUDIO_FILE = auto()
