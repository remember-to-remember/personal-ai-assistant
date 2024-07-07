""" Module for whatsapp for business wrapper. """

import json

import httpx
from structlog import get_logger

from backend.api import config
from backend.api.messaging_provider_wrapper import MessagingProviderWrapper


class WhatsappForBusinessWrapper(MessagingProviderWrapper):
    """Class for whatsapp for business wrapper."""

    async def process_initial_connection(
        self,
        body: dict,
    ) -> tuple[str, str | None]:
        """Process initial connection."""

        logger = get_logger().bind(body=json.dumps(body, indent=2))
        logger.info("Started process initial connection")

        mode = body.get("hub.mode")
        token = body.get("hub.verify_token")
        challenge = body.get("hub.challenge")

        logger.info("Completed process incoming message")
        if mode == "subscribe":
            return token, challenge
        return token, None

    async def extract_incomging_message(
        self,
        body: dict,
    ) -> str:
        """Extract incoming message."""

        logger = get_logger().bind(body=json.dumps(body, indent=2))
        logger.info("Started extract incoming message")

        messages = (
            body.get("entry", [])[0]
            .get("changes", [])[0]
            .get("value", {})
            .get("messages", [])
        )

        instant_message = None
        if messages and len(messages) > 0 and messages[0].get("type") == "text":
            instant_message = messages[0].get("text", {}).get("body")

        logger.info("Completed extract incoming message")
        return instant_message

    async def reply_outgoing_message(
        self,
        reply_message: str,
        body: dict,
    ) -> dict:
        """Reply outgoing message."""

        logger = get_logger().bind(
            reply_message=reply_message, body=json.dumps(body, indent=2)
        )
        logger.info("Started Reply outgoing message")

        if reply_message:
            messages = (
                body.get("entry", [])[0]
                .get("changes", [])[0]
                .get("value", {})
                .get("messages", [])
            )
            if messages and len(messages) > 0 and messages[0].get("type") == "text":
                message = messages[0]
                business_phone_number_id = (
                    body.get("entry", [])[0]
                    .get("changes", [])[0]
                    .get("value", {})
                    .get("metadata", {})
                    .get("phone_number_id")
                )

                reply_url = f"https://graph.facebook.com/v20.0/{business_phone_number_id}/messages"
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        reply_url,
                        headers={
                            "Authorization": f"Bearer {config.CONFIG.whatsapp_for_business_api_token}"
                        },
                        json={
                            "messaging_product": "whatsapp",
                            "to": message.get("from"),
                            "text": {
                                # "body": f"Echo: {message.get('text', {}).get('body')}"
                                "body": reply_message
                            },
                            "context": {
                                "message_id": message.get(
                                    "id"
                                )  # Shows the message as a reply to the original user message
                            },
                        },
                    )
                    if response.status_code != 200:
                        logger.info("Completed process incoming message")
                        raise Exception("Failed to send reply message")

                    read_url = f"https://graph.facebook.com/v20.0/{business_phone_number_id}/messages"
                    await client.post(
                        read_url,
                        headers={
                            "Authorization": f"Bearer {config.CONFIG.whatsapp_for_business_api_token}"
                        },
                        json={
                            "messaging_product": "whatsapp",
                            "status": "read",
                            "message_id": message.get("id"),
                        },
                    )

        logger.info("Completed process incoming message")
        return {"status": "success"}
