"""The one place a Claude client is built. Platform: Claude on Microsoft Foundry (docs/DECISIONS.md §5)."""

from __future__ import annotations

import os

import anthropic


def foundry_client() -> anthropic.AnthropicFoundry:
    """Reads FOUNDRY_API_KEY and FOUNDRY_RESOURCE (the Foundry resource name) from the environment."""
    return anthropic.AnthropicFoundry(
        api_key=os.environ["FOUNDRY_API_KEY"],
        resource=os.environ["FOUNDRY_RESOURCE"],
    )
