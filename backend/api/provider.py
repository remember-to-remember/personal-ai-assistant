""" Module for providers. """

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from structlog import get_logger

from backend.api import config
from backend.api.data_repositories.mongo_db import MongoDB
from backend.api.data_repositories.sqlite import SQLite
from backend.api.data_repository import DataRepository
from backend.api.enum import (
    DataRepositoryType,
    InferenceProviderType,
    MessagingProviderType,
)
from backend.api.inference_provider_wrapper import InferenceProviderWrapper
from backend.api.inference_provider_wrappers.in_process_inference import (
    InProcessInference,
)
from backend.api.messaging_provider_wrapper import MessagingProviderWrapper
from backend.api.messaging_provider_wrappers.whatsapp_business_wrapper import (
    WhatsappForBusinessWrapper,
)


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Providers:
    """Class for storing providers."""

    data_repository: DataRepository
    messaging_provider_wrapper: MessagingProviderWrapper
    inference_provider_wrapper: InferenceProviderWrapper


PROVIDERS: Providers = None


def configure_providers() -> None:
    """Configure providers."""

    logger = get_logger().bind(
        DataRepositoryType=config.CONFIG.data_repository_type,
        InferenceProviderType=config.CONFIG.inference_provider_type,
    )
    logger.info("Starting configure providers")
    global PROVIDERS
    PROVIDERS = Providers(
        data_repository=_get_data_repository(config.CONFIG.data_repository_type),
        messaging_provider_wrapper=_get_messaging_provider_wrapper(
            config.CONFIG.messaging_provider_type
        ),
        inference_provider_wrapper=_get_inference_provider_wrapper(
            config.CONFIG.inference_provider_type
        ),
    )

    logger.info("Completed configure providers")


def _get_data_repository(enum_type: DataRepositoryType) -> DataRepository:
    match enum_type:
        case DataRepositoryType.SQLITE:
            return SQLite()
        case DataRepositoryType.MONGO_DB:
            return MongoDB()


def _get_messaging_provider_wrapper(
    enum_type: MessagingProviderType,
) -> MessagingProviderWrapper:
    match enum_type:
        case MessagingProviderType.WHATSAPP_FOR_BUSINESS:
            return WhatsappForBusinessWrapper()


def _get_inference_provider_wrapper(
    enum_type: InferenceProviderType,
) -> InferenceProviderWrapper:
    match enum_type:
        case InferenceProviderType.IN_PROCESS:
            return InProcessInference()
