""" Module for command line interface (cli). """

import dataclasses
import json

from structlog import get_logger

from backend.api import config, provider
from backend.api.entities import Caller, Chat, ChatInputModel
from backend.api.lib import (
    configure_global_logging_level,
    log_config_settings,
    parse_cli_args_with_defaults,
    parse_env_vars_with_defaults,
)
from backend.api.provider import configure_providers


async def get_caller(idp_id: str):
    """Get caller."""

    return await provider.PROVIDERS.data_repository.load_caller(idp_id)


async def process_chat(chat_input: ChatInputModel, caller: Caller) -> Chat:
    """Process chat."""

    logger = get_logger().bind(
        job_request=(
            chat_input.model_dump(exclude=chat_input.get_exclude_fields_for_logging())
            if chat_input
            else None
        ),
        caller=(
            {
                k: str(v)
                for k, v in caller.__dict__.items()
                if k not in Caller.get_exclude_fields_for_logging()
            }
            if caller
            else None
        ),
    )
    logger.info("Starting process chat")

    chat_input = Chat(**chat_input.model_dump())
    chat_input.caller_id = caller.caller_id
    chat_output = await request_for_inference(chat_input.caller_chat_text)

    # provider.PROVIDERS.data_repository.save_job(chat_output, caller=caller)

    logger.info("Completed process chat")
    return chat_output


async def process_initial_connection(
    body: dict,
) -> str | None:
    """Process initial connection."""

    logger = get_logger().bind(body=json.dumps(body, indent=2))
    logger.info("Started process initial connection")

    token, response = (
        await provider.PROVIDERS.messaging_provider_wrapper.process_initial_connection(
            body
        )
    )

    logger.info("Completed process initial connection")
    if token and response:
        caller = await get_caller(token)
        if caller:
            return response
    return None


async def process_incoming_message(body: dict) -> dict:
    """Process incomging message."""

    instant_message = (
        await provider.PROVIDERS.messaging_provider_wrapper.extract_incomging_message(
            body
        )
    )

    reply_message = None
    if instant_message:
        reply_message = await request_for_inference(instant_message)
        # reply_message = f"Echo: {instant_message}"

    return await provider.PROVIDERS.messaging_provider_wrapper.reply_outgoing_message(
        reply_message, body
    )


async def request_for_inference(prompt_text: str) -> str:
    """Request for inference."""

    return await provider.PROVIDERS.inference_provider_wrapper.request_for_inference(
        prompt_text
    )


def init() -> None:
    """Entry point if called as an executable."""

    logger = get_logger()
    logger.info("Starting init from main")

    # set configuration based on environment variables and cli arguments
    cli_args = parse_cli_args_with_defaults()
    env_vars = parse_env_vars_with_defaults()
    all_values = dataclasses.asdict(env_vars) | dataclasses.asdict(cli_args)
    config.CONFIG = config.Config(**all_values)
    configure_global_logging_level(config.CONFIG.debug_mode)
    log_config_settings(config.CONFIG)

    # configure providers based on the above configuration
    configure_providers()

    logger.info("Completed init from main")


if __name__ == "__main__":
    init()
