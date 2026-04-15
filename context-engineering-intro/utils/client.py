"""
utils/client.py

Shared Anthropic client setup used by all examples.
Loads your API key from .env automatically.
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load .env file from the project root
load_dotenv()

# The model we use throughout this project
MODEL = "claude-haiku-4-5-20251001"  # Fast and cheap — great for learning

def get_client() -> Anthropic:
    """Return a configured Anthropic client."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY not found.\n"
            "1. Copy .env.example to .env\n"
            "2. Add your key from https://console.anthropic.com/"
        )
    return Anthropic(api_key=api_key)


def simple_chat(messages: list, system: str = "") -> str:
    """
    Send a messages list to the API and return the text response.

    Args:
        messages: List of {"role": ..., "content": ...} dicts
        system:   Optional system prompt string

    Returns:
        The model's response as a plain string
    """
    client = get_client()
    kwargs = {
        "model": MODEL,
        "max_tokens": 1024,
        "messages": messages,
    }
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)
    return response.content[0].text
