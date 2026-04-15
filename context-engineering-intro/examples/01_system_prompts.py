"""
Lesson 01: System Prompts
=========================

WHAT YOU'LL LEARN:
  The system prompt is the most powerful part of your context.
  It sets the model's persona, rules, and tone before the user
  says anything. Same user question, completely different answers
  depending on the system prompt.

CONCEPT:
  Every API call has two "layers":
    - system:   Instructions for the model (it reads these first)
    - messages: The actual conversation

  The system prompt is like the job description you give a new
  employee before they take their first call.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.client import simple_chat

# ── The same user question ───────────────────────────────────────────────────

USER_QUESTION = "I'm having trouble logging in to my account."

# ── Three different system prompts ───────────────────────────────────────────

SYSTEM_DEFAULT = ""  # No system prompt at all

SYSTEM_SUPPORT_AGENT = """
You are Maya, a friendly customer support agent for Acme SaaS.
Your job is to help users solve problems quickly and kindly.
Always:
- Greet the user warmly by acknowledging their issue
- Ask one clarifying question before jumping to solutions
- Keep replies under 3 sentences
Never mention competitors or discuss pricing.
""".strip()

SYSTEM_SECURITY_FOCUSED = """
You are a security-conscious support bot for a banking application.
Treat every login issue as a potential security event.
Always:
- Ask the user to verify their identity before proceeding
- Remind them never to share passwords
- Recommend enabling two-factor authentication
Be professional but cautious. Never assume the user is who they say they are.
""".strip()


def demo_system_prompts():
    print("=" * 60)
    print("LESSON 01: System Prompts")
    print("=" * 60)
    print(f'\nSame user message: "{USER_QUESTION}"\n')

    configs = [
        ("No system prompt", SYSTEM_DEFAULT),
        ("Friendly support agent (Maya)", SYSTEM_SUPPORT_AGENT),
        ("Security-focused banking bot", SYSTEM_SECURITY_FOCUSED),
    ]

    for label, system in configs:
        print(f"\n{'─' * 50}")
        print(f"SYSTEM PROMPT: {label}")
        print(f"{'─' * 50}")

        messages = [{"role": "user", "content": USER_QUESTION}]
        reply = simple_chat(messages, system=system)
        print(reply)

    # ── Interactive section ───────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("YOUR TURN — Try writing your own system prompt")
    print("=" * 60)
    print("Type a system prompt (or press Enter to skip):\n")

    custom_system = input("> ").strip()
    if custom_system:
        messages = [{"role": "user", "content": USER_QUESTION}]
        reply = simple_chat(messages, system=custom_system)
        print(f"\nModel response:\n{reply}")

    print("\n✅ Lesson 01 complete! Key takeaway:")
    print("   The system prompt shapes everything. It's the single")
    print("   highest-leverage piece of context you control.\n")


if __name__ == "__main__":
    demo_system_prompts()
