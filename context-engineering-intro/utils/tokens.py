"""
utils/tokens.py

Simple token counting helpers.

Tokens are the unit the API charges by and enforces limits on.
Roughly: 1 token ≈ 4 characters ≈ 0.75 words in English.
"""


def estimate_tokens(text: str) -> int:
    """
    Rough token estimate without calling the API.
    Good enough for budgeting — uses the ~4 chars/token heuristic.
    """
    return len(text) // 4


def estimate_history_tokens(history: list) -> int:
    """Estimate the total tokens in a messages list."""
    total = 0
    for msg in history:
        total += estimate_tokens(msg.get("content", ""))
        total += 4  # overhead per message (role label, formatting)
    return total


def history_fits(history: list, system: str = "", max_tokens: int = 180_000) -> bool:
    """
    Returns True if the history + system prompt is safely under the limit.
    Default limit is conservative — leaves room for the model's reply.
    """
    used = estimate_history_tokens(history) + estimate_tokens(system)
    return used < max_tokens


def token_budget_report(history: list, system: str = "") -> None:
    """Print a simple token usage summary."""
    history_tokens = estimate_history_tokens(history)
    system_tokens = estimate_tokens(system)
    total = history_tokens + system_tokens
    limit = 200_000

    print(f"\n── Token Budget ────────────────")
    print(f"  System prompt : ~{system_tokens:,} tokens")
    print(f"  History       : ~{history_tokens:,} tokens")
    print(f"  Total used    : ~{total:,} / {limit:,} tokens")
    print(f"  Remaining     : ~{limit - total:,} tokens")
    print(f"────────────────────────────────\n")
