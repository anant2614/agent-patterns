"""Factory for the chat client used by every pattern.

We default to Azure OpenAI authenticated via `AzureCliCredential` (so no secrets
in code). If `AZURE_OPENAI_API_KEY` is set we fall back to API-key auth — useful
in CI where AAD is awkward.
"""

from __future__ import annotations

import os
from functools import lru_cache

from agent_framework.openai import OpenAIChatClient
from azure.identity import AzureCliCredential, ChainedTokenCredential, EnvironmentCredential
from dotenv import load_dotenv

load_dotenv()


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Environment variable {name!r} is required. "
            f"Copy .env.example to .env and fill it in, or export it in your shell."
        )
    return value


@lru_cache(maxsize=1)
def get_chat_client(model: str | None = None) -> OpenAIChatClient:
    """Return a configured chat client targeting Azure OpenAI.

    Args:
        model: Override the Azure deployment name. Defaults to AZURE_OPENAI_DEPLOYMENT.

    Auth strategy:
        1. If AZURE_OPENAI_API_KEY is set → use it.
        2. Otherwise → AAD via ChainedTokenCredential(EnvironmentCredential, AzureCliCredential).
           Run `az login` once on your machine.
    """
    endpoint = _required("AZURE_OPENAI_ENDPOINT")
    deployment = model or _required("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")

    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if api_key:
        return OpenAIChatClient(
            model=deployment,
            azure_endpoint=endpoint,
            api_version=api_version,
            api_key=api_key,
        )

    credential = ChainedTokenCredential(EnvironmentCredential(), AzureCliCredential())
    return OpenAIChatClient(
        model=deployment,
        azure_endpoint=endpoint,
        api_version=api_version,
        credential=credential,
    )
