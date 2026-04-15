"""
Lesson 05: Structured Output
==============================

WHAT YOU'LL LEARN:
  By default, models reply in free-form prose. But for real apps,
  you usually need data you can actually *use* in code — JSON, not
  paragraphs. You can engineer the context to reliably produce
  structured, parseable output.

CONCEPT:
  Three techniques, increasingly reliable:
    1. Ask nicely in the prompt ("reply in JSON")
    2. Show an example JSON in the prompt (few-shot)
    3. Start the assistant's reply yourself to force the format

  Technique 3 — "prefilling" the assistant turn — is the most
  reliable because the model just has to continue what it started.
"""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.client import get_client, MODEL

client = get_client()

SYSTEM = "You are a data extraction assistant. Always reply with valid JSON only. No prose, no markdown fences."

RAW_REVIEW = """
Bought this blender last month. The motor is incredibly powerful — blended
frozen fruit in under 10 seconds, no problem. The noise level is honestly
shocking though, loud enough that my neighbours knocked. Cleanup is a breeze
because the blade assembly detaches completely. Paid $89 which feels fair
given the build quality. Would buy again despite the noise.
"""


def technique_1_ask_nicely(review: str) -> dict | None:
    """Simple instruction — works sometimes, fails silently other times."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=SYSTEM,
        messages=[
            {
                "role": "user",
                "content": (
                    "Extract the following fields from this product review as JSON: "
                    "product_type, sentiment (positive/negative/mixed), pros (list), "
                    "cons (list), price_mentioned, would_recommend (bool).\n\n"
                    f"Review:\n{review}"
                ),
            }
        ],
    )
    raw = response.content[0].text.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print(f"  ⚠️  Parse failed. Model returned:\n  {raw[:200]}")
        return None


def technique_2_few_shot(review: str) -> dict | None:
    """Show an example of the exact JSON shape we want."""
    example_review = "Great headphones, amazing sound quality. Too expensive though at $300. Wouldn't buy again."
    example_output = json.dumps({
        "product_type": "headphones",
        "sentiment": "mixed",
        "pros": ["amazing sound quality"],
        "cons": ["too expensive"],
        "price_mentioned": 300,
        "would_recommend": False,
    }, indent=2)

    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=SYSTEM,
        messages=[
            # Show the example
            {"role": "user", "content": f"Extract fields from this review:\n{example_review}"},
            {"role": "assistant", "content": example_output},
            # Real question
            {"role": "user", "content": f"Extract fields from this review:\n{review}"},
        ],
    )
    raw = response.content[0].text.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print(f"  ⚠️  Parse failed. Model returned:\n  {raw[:200]}")
        return None


def technique_3_prefill(review: str) -> dict | None:
    """
    Prefill the assistant's reply with '{' to force JSON output.

    We add a partial assistant message to the history, and the model
    must continue from there. Since it's already started a JSON object,
    it almost always finishes it properly.
    """
    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=SYSTEM,
        messages=[
            {
                "role": "user",
                "content": (
                    "Extract: product_type, sentiment, pros (list), cons (list), "
                    "price_mentioned, would_recommend (bool) from this review:\n\n"
                    f"{review}"
                ),
            },
            # 👇 This is the prefill — we start the assistant's reply
            {"role": "assistant", "content": "{"},
        ],
    )
    # The model continues from '{', so we prepend it back
    raw = "{" + response.content[0].text.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print(f"  ⚠️  Parse failed. Model returned:\n  {raw[:200]}")
        return None


def demo_structured_output():
    print("=" * 60)
    print("LESSON 05: Structured Output")
    print("=" * 60)
    print(f"\nReview to extract:\n{'─'*40}")
    print(RAW_REVIEW.strip())
    print("─" * 40)

    techniques = [
        ("1. Ask nicely", technique_1_ask_nicely),
        ("2. Few-shot example", technique_2_few_shot),
        ("3. Prefill assistant turn", technique_3_prefill),
    ]

    for name, fn in techniques:
        print(f"\n\nTechnique {name}")
        print("─" * 40)
        result = fn(RAW_REVIEW)
        if result:
            print("✅ Valid JSON parsed:")
            print(json.dumps(result, indent=2))
        else:
            print("❌ Failed to produce parseable JSON")

    # ── Interactive section ───────────────────────────────────────────────────
    print("\n\n" + "=" * 60)
    print("YOUR TURN — Paste your own product review")
    print("(or press Enter to skip)")
    print("=" * 60)
    user_review = input("> ").strip()
    if user_review:
        result = technique_3_prefill(user_review)
        if result:
            print("\n✅ Extracted JSON:")
            print(json.dumps(result, indent=2))

    print("\n✅ Lesson 05 complete! Key takeaway:")
    print("   Prefilling the assistant turn is the most reliable way")
    print("   to force structured output without special tooling.\n")


if __name__ == "__main__":
    demo_structured_output()
