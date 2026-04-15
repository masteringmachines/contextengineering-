"""
utils/history.py

Helpers for managing conversation history — the list of messages
you send to the API to give the model memory of past turns.
"""


def add_user_message(history: list, content: str) -> list:
    """Append a user message and return the updated history."""
    return history + [{"role": "user", "content": content}]


def add_assistant_message(history: list, content: str) -> list:
    """Append an assistant message and return the updated history."""
    return history + [{"role": "assistant", "content": content}]


def get_last_reply(history: list) -> str:
    """Return the most recent assistant message, or empty string."""
    for msg in reversed(history):
        if msg["role"] == "assistant":
            return msg["content"]
    return ""


def trim_to_last_n_turns(history: list, n: int) -> list:
    """
    Keep only the most recent N full turns (user + assistant pairs).
    Useful for staying within token limits on long conversations.

    A "turn" = one user message + one assistant reply = 2 items.
    """
    max_messages = n * 2
    if len(history) <= max_messages:
        return history
    return history[-max_messages:]


def pretty_print(history: list) -> None:
    """Print a conversation history in a readable format."""
    for msg in history:
        role = msg["role"].upper()
        print(f"\n{'─' * 40}")
        print(f"[{role}]")
        print(msg["content"])
    print(f"\n{'─' * 40}")
