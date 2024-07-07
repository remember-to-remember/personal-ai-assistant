""" Module for in process inference. """

import os

import torch
import transformers
from structlog import get_logger

from backend.api.inference_provider_wrapper import InferenceProviderWrapper

# os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

# https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct
MODEL_ID = "meta-llama/Meta-Llama-3.1-8B-Instruct"

PIPELINE = transformers.pipeline(
    "text-generation",
    model=MODEL_ID,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
)


class InProcessInference(InferenceProviderWrapper):
    """Class for in process inference."""

    async def request_for_inference(
        self,
        instant_message: str,
    ) -> str:
        """Request for inference."""

        logger = get_logger().bind(instant_message=instant_message)
        logger.info("Started request for inference")

        prompt = {
            "role": "assistant",
            # "content": f"You are a compassionate person who is trying very hard to help! {instant_message}",
            "content": instant_message,
        }

        outputs = PIPELINE(
            [prompt],
            max_new_tokens=256,
        )

        return outputs[0]["generated_text"][-1]["content"]
