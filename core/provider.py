""" Module for providers. """

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from structlog import get_logger

from core import config
from core.data_repositories.mongo_db import MongoDB
from core.data_repository import DataRepository
from core.enum import DataRepositoryType, InferenceProviderType, MessagingProviderType
from core.inference_provider_wrapper import InferenceProviderWrapper
from core.inference_provider_wrappers.llm_llama_instruct_wrapper import (
    LLMLlamaIntructWrapper,
)
from core.messaging_provider_wrapper import MessagingProviderWrapper
from core.messaging_provider_wrappers.whatsapp_business_wrapper import (
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
        case InferenceProviderType.LLM_LLAMA_INSTRUCT:
            return LLMLlamaIntructWrapper()
