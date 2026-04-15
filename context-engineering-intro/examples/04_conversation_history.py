"""
Lesson 04: Conversation History
================================

WHAT YOU'LL LEARN:
  The API has no memory between calls — it's completely stateless.
  To make a "chatbot that remembers," you must manually send the
  full conversation history on every API call.

  This lesson shows you how to build and manage that history list,
  and what happens if you forget to include it.

CONCEPT:
  Each call needs the full messages list so far:
    Turn 1: [user_msg_1]                     → reply_1
    Turn 2: [user_msg_1, reply_1, user_msg_2] → reply_2
    Turn 3: [user_msg_1, reply_1, user_msg_2, reply_2, user_msg_3] → reply_3

  You build this list yourself. The model can't look back at prior
  calls — only at what you explicitly pass in.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.client import simple_chat, get_client, MODEL
from utils.history import add_user_message, add_assistant_message, pretty_print

SYSTEM = """
You are a helpful cooking assistant named Jules.
You remember everything discussed in the conversation.
Keep answers friendly and brief.
""".strip()


def chat_without_history():
    """
    Demonstrates the "stateless" problem: each call starts fresh.
    The model cannot answer follow-up questions because it has no memory.
    """
    print("\n❌ WITHOUT conversation history:")
    print("─" * 40)

    client = get_client()

    # Turn 1
    r1 = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=SYSTEM,
        messages=[{"role": "user", "content": "My favourite ingredient is miso."}],
    )
    print(f"User: My favourite ingredient is miso.")
    print(f"Jules: {r1.content[0].text}\n")

    # Turn 2 — we DON'T send prior history, so the model has no idea
    r2 = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=SYSTEM,
        messages=[{"role": "user", "content": "Can you suggest a recipe using my favourite ingredient?"}],
    )
    print(f"User: Can you suggest a recipe using my favourite ingredient?")
    print(f"Jules: {r2.content[0].text}")
    print("\n(Notice: Jules has no idea what your favourite ingredient is!)")


def chat_with_history():
    """
    Demonstrates proper history management.
    Each turn appends to the list, which is sent in full each time.
    """
    print("\n\n✅ WITH conversation history:")
    print("─" * 40)

    history = []
    client = get_client()

    def send(user_input: str) -> str:
        nonlocal history
        history = add_user_message(history, user_input)
        response = client.messages.create(
            model=MODEL,
            max_tokens=300,
            system=SYSTEM,
            messages=history,
        )
        reply = response.content[0].text
        history = add_assistant_message(history, reply)
        return reply

    # Scripted conversation to show memory working
    turns = [
        "My favourite ingredient is miso.",
        "Can you suggest a recipe using my favourite ingredient?",
        "How long does that take to make?",
        "Great — what did you say my favourite ingredient was again?",
    ]

    for msg in turns:
        reply = send(msg)
        print(f"User : {msg}")
        print(f"Jules: {reply}\n")

    print(f"Final history has {len(history)} messages across {len(history)//2} turns.")


def interactive_chat():
    """A live multi-turn chat loop you can try yourself."""
    print("\n\n💬 Interactive chat with Jules (type 'quit' to exit)")
    print("─" * 40)

    history = []
    client = get_client()

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if not user_input:
            continue

        history = add_user_message(history, user_input)
        response = client.messages.create(
            model=MODEL,
            max_tokens=400,
            system=SYSTEM,
            messages=history,
        )
        reply = response.content[0].text
        history = add_assistant_message(history, reply)
        print(f"Jules: {reply}\n")

    print(f"\n(Conversation had {len(history) // 2} turns)")


def demo_conversation_history():
    print("=" * 60)
    print("LESSON 04: Conversation History")
    print("=" * 60)

    chat_without_history()
    chat_with_history()

    print("\n" + "=" * 60)
    print("YOUR TURN — Have a real conversation with Jules")
    print("(type 'quit' to exit)")
    print("=" * 60)
    interactive_chat()

    print("\n✅ Lesson 04 complete! Key takeaway:")
    print("   The model is stateless. You are the memory.")
    print("   Always send the full history on every API call.\n")


if __name__ == "__main__":
    demo_conversation_history()
