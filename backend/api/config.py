""" Module for configuration settings. """

from pydantic.dataclasses import dataclass

from backend.api.enum import (
    DataRepositoryType,
    InferenceProviderType,
    MessagingProviderType,
)


@dataclass
class Config:
    """Class for storing configuration settings."""

    # cli args
    debug_mode: bool

    # api
    conversation_api_port: int
    conversation_api_reload: bool

    # auth0
    auth0_public_key: str
    auth0_issuer: str
    auth0_audience: str

    # data repository
    data_repository_type: DataRepositoryType
    run_db_migrations: bool

    # sqlite
    sqlite_connection_string: str

    # mongodb
    mongodb_connection_string: str

    # messsaging
    messaging_provider_type: MessagingProviderType

    # whatsapp for business
    whatsapp_for_business_api_token: str

    # inference
    inference_provider_type: InferenceProviderType


CONFIG: Config = None
