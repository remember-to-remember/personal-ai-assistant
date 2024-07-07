""" Module for inference provider wrapper. """

from abc import ABC, abstractmethod


class InferenceProviderWrapper(ABC):
    """Class for inference provider wrapper."""

    @abstractmethod
    def request_for_inference(
        self,
        instant_message: str,
    ):
        """Request for inference."""
