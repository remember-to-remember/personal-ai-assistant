""" Module for configuration settings. """

from pydantic.dataclasses import dataclass

from core.enum import DataRepositoryType, InferenceProviderType, MessagingProviderType


@dataclass
class Config:
    """Class for storing configuration settings."""

    # cli args
    debug_mode: bool

    # api
    api_port: int
    api_reload: bool

    # data repository
    data_repository_type: DataRepositoryType
    run_db_migrations: bool

    # mongodb
    mongodb_connection_string: str

    # messsaging
    messaging_provider_type: MessagingProviderType

    # whatsapp for business
    whatsapp_for_business_api_token: str

    # inference
    inference_provider_type: InferenceProviderType


CONFIG: Config = None
