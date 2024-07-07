""" Module for messaging provider wrapper. """

from abc import ABC, abstractmethod


class MessagingProviderWrapper(ABC):
    """Class for messaging provider wrapper."""

    @abstractmethod
    async def process_initial_connection(
        self,
        body: dict,
    ) -> tuple[str, str | None]:
        """Process initial connection."""

    @abstractmethod
    async def extract_incomging_message(
        self,
        body: dict,
    ) -> str:
        """Extract incoming message."""

    @abstractmethod
    async def reply_outgoing_message(
        self,
        reply_message: str,
        body: dict,
    ) -> dict:
        """Reply outgoing message."""
