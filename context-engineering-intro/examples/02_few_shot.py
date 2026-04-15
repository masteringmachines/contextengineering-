"""
Lesson 02: Few-Shot Examples
============================

WHAT YOU'LL LEARN:
  Instead of writing long instructions, you can *show* the model
  what you want by including examples directly in the context.
  This is called "few-shot prompting" — and it often works better
  than paragraphs of instructions.

CONCEPT:
  "Few-shot" means providing a few input/output examples before
  your real question. The model infers the pattern and applies it.

  Zero-shot: Just ask, no examples
  One-shot:  One example
  Few-shot:  2–5 examples (sweet spot for most tasks)

  Examples go in the messages array as fake prior conversation turns.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.client import simple_chat

SYSTEM = "You are a helpful assistant that classifies customer feedback."


def classify_zero_shot(feedback: str) -> str:
    """Classify with instructions only — no examples."""
    messages = [
        {
            "role": "user",
            "content": (
                "Classify this customer feedback as POSITIVE, NEGATIVE, or NEUTRAL. "
                "Reply with only the label.\n\n"
                f"Feedback: {feedback}"
            ),
        }
    ]
    return simple_chat(messages, system=SYSTEM)


def classify_few_shot(feedback: str) -> str:
    """
    Classify by showing examples first.

    Notice how we build a fake conversation history where the model
    has already seen labeled examples. This teaches the format and
    the judgment calls we want, without lengthy instructions.
    """
    messages = [
        # Example 1
        {
            "role": "user",
            "content": "Feedback: The product arrived damaged and support never replied.",
        },
        {"role": "assistant", "content": "NEGATIVE"},
        # Example 2
        {
            "role": "user",
            "content": "Feedback: It does what it says. Nothing special.",
        },
        {"role": "assistant", "content": "NEUTRAL"},
        # Example 3
        {
            "role": "user",
            "content": "Feedback: I've tried 6 other tools and this is the only one that actually worked for my team.",
        },
        {"role": "assistant", "content": "POSITIVE"},
        # Example 4 — a tricky one with mixed signals
        {
            "role": "user",
            "content": "Feedback: Great features but the onboarding is really confusing.",
        },
        {"role": "assistant", "content": "NEUTRAL"},
        # Now the real question
        {"role": "user", "content": f"Feedback: {feedback}"},
    ]
    return simple_chat(messages, system=SYSTEM)


def demo_few_shot():
    print("=" * 60)
    print("LESSON 02: Few-Shot Examples")
    print("=" * 60)

    test_cases = [
        "Honestly couldn't be happier. Renewed for another year immediately.",
        "Charged me twice and it took 3 weeks to get a refund.",
        "Works fine. Does the job.",
        "The new UI is beautiful but I lost all my saved settings after the update.",
    ]

    print("\nComparing zero-shot vs few-shot classification:\n")

    for feedback in test_cases:
        zero = classify_zero_shot(feedback)
        few = classify_few_shot(feedback)
        match = "✅" if zero.strip() == few.strip() else "🔀"

        print(f"Feedback: \"{feedback[:60]}...\"" if len(feedback) > 60 else f"Feedback: \"{feedback}\"")
        print(f"  Zero-shot : {zero.strip()}")
        print(f"  Few-shot  : {few.strip()}  {match}")
        print()

    # ── Interactive section ───────────────────────────────────────────────────
    print("=" * 60)
    print("YOUR TURN — Paste your own feedback to classify")
    print("(or press Enter to skip)")
    print("=" * 60)

    user_input = input("> ").strip()
    if user_input:
        result = classify_few_shot(user_input)
        print(f"\nFew-shot classification: {result.strip()}")

    print("\n✅ Lesson 02 complete! Key takeaway:")
    print("   Examples in context are often more reliable than")
    print("   instructions. Show, don't just tell.\n")


if __name__ == "__main__":
    demo_few_shot()
