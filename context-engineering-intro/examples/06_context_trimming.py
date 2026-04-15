"""
Lesson 06: Context Limits & Trimming
======================================

WHAT YOU'LL LEARN:
  The context window is large (200k tokens for claude-sonnet-4-5)
  but not infinite. Long conversations will eventually hit the limit.
  You need a strategy for what to keep and what to drop.

CONCEPT:
  Three common trimming strategies:

    1. Sliding window  — keep only the last N turns, drop the rest
    2. Summarisation   — compress old turns into a summary, keep recent turns
    3. Selective keep  — always keep certain messages (system-critical info)

  Strategy 2 is the most powerful: you lose no important information,
  just compress it. This lesson shows all three.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.client import simple_chat, get_client, MODEL
from utils.history import add_user_message, add_assistant_message
from utils.tokens import estimate_history_tokens, token_budget_report

client = get_client()

# ── Simulated long conversation ───────────────────────────────────────────────

def build_long_history() -> list:
    """Build a realistic 10-turn conversation to demonstrate trimming."""
    turns = [
        ("user", "I'm planning a trip to Japan in April. Any tips?"),
        ("assistant", "April is cherry blossom season — one of the best times to visit! I'd recommend Tokyo, Kyoto, and Osaka as a classic triangle route. Kyoto's Maruyama Park and the Philosopher's Path are spectacular for sakura."),
        ("user", "How many days should I spend in Kyoto?"),
        ("assistant", "3–4 days is ideal for Kyoto. That gives you time for Arashiyama, Fushimi Inari, the Geisha district in Gion, and at least one day-trip to Nara to see the deer."),
        ("user", "What's the best way to get from Tokyo to Kyoto?"),
        ("assistant", "The Shinkansen (bullet train) is by far the best option. The Nozomi takes about 2h15m and costs around ¥13,500. Get an IC card like Suica for all local transport once you're there."),
        ("user", "I'm vegetarian — will I find enough food options?"),
        ("assistant", "Japan can be tricky for vegetarians since dashi (fish stock) is used in many broths. That said, Buddhist temple cuisine (shojin ryori) is 100% plant-based, and cities have growing vegan scenes. Apps like HappyCow will be your best friend."),
        ("user", "What about budget? Is Japan expensive?"),
        ("assistant", "Japan is more affordable than people expect. Budget ¥10,000–15,000/day ($65–100) for accommodation, food, and local transport outside of attractions. The Shinkansen is a big one-time cost. Convenience stores (7-Eleven, FamilyMart) have excellent cheap meals."),
        ("user", "Should I get a JR Pass?"),
        ("assistant", "For a Tokyo-Kyoto-Osaka trip, the JR Pass often isn't worth it unless you're doing 3+ Shinkansen journeys. Do the math: one Tokyo→Kyoto Shinkansen is ¥13,500 each way. A 7-day JR Pass is ¥50,000. Calculate based on your specific itinerary."),
        ("user", "What's one thing most tourists miss?"),
        ("assistant", "Staying in a traditional ryokan (Japanese inn) for at least one night. The multi-course kaiseki dinner, tatami rooms, and outdoor onsen experience is unlike anything else — and usually includes breakfast. It changes how you see the whole trip."),
        ("user", "Perfect. Now, given all we've discussed — what's my ideal 10-day itinerary?"),
        ("assistant", "Based on everything: Days 1–3 Tokyo (Shinjuku, Shibuya, teamLab, day-trip to Nikko). Day 4 Shinkansen to Kyoto. Days 4–7 Kyoto (Arashiyama, Fushimi Inari, Gion, ryokan night, day-trip to Nara). Days 8–9 Osaka (Dotonbori, Kuromon Market, Osaka Castle). Day 10 fly home from Osaka or back to Tokyo."),
    ]
    return [{"role": role, "content": content} for role, content in turns]


# ── Strategy 1: Sliding window ────────────────────────────────────────────────

def sliding_window(history: list, keep_last_n_turns: int) -> list:
    """Drop oldest messages, keep only the most recent N turns."""
    max_msgs = keep_last_n_turns * 2
    return history[-max_msgs:] if len(history) > max_msgs else history


# ── Strategy 2: Summarise old turns ──────────────────────────────────────────

def summarise_and_trim(history: list, keep_recent_n_turns: int) -> list:
    """
    Compress everything except the last N turns into a summary,
    then inject that summary as context at the start.
    """
    cutoff = len(history) - (keep_recent_n_turns * 2)
    if cutoff <= 0:
        return history  # Nothing old enough to summarise

    old = history[:cutoff]
    recent = history[cutoff:]

    # Build a conversation text to summarise
    old_text = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in old
    )

    summary = simple_chat(
        messages=[
            {
                "role": "user",
                "content": (
                    "Summarise this conversation in 3–5 bullet points, "
                    "preserving all key facts and decisions:\n\n" + old_text
                ),
            }
        ]
    )

    # Inject the summary as a user message at the start of recent history
    summary_msg = {
        "role": "user",
        "content": f"[Earlier conversation summary]\n{summary}\n[End summary]",
    }
    summary_ack = {
        "role": "assistant",
        "content": "Understood. I have the context from our earlier discussion.",
    }

    return [summary_msg, summary_ack] + recent


# ── Demo ─────────────────────────────────────────────────────────────────────

def demo_context_trimming():
    print("=" * 60)
    print("LESSON 06: Context Limits & Trimming")
    print("=" * 60)

    history = build_long_history()
    follow_up = "Based on our conversation, what's the single most important tip you'd give me?"

    print(f"\nBuilt a {len(history)}-message ({len(history)//2}-turn) conversation.")
    token_budget_report(history)

    # ── Strategy 1 ───────────────────────────────────────────────────────────
    print("STRATEGY 1: Sliding window (keep last 3 turns)\n" + "─" * 40)
    windowed = sliding_window(history, keep_last_n_turns=3)
    windowed = add_user_message(windowed, follow_up)
    reply_1 = simple_chat(windowed)
    print(f"Messages sent to API: {len(windowed)} (was {len(history)+1})")
    print(f"Response: {reply_1}\n")

    # ── Strategy 2 ───────────────────────────────────────────────────────────
    print("\nSTRATEGY 2: Summarise old + keep last 3 turns\n" + "─" * 40)
    summarised = summarise_and_trim(history, keep_recent_n_turns=3)
    print(f"Messages after summarisation: {len(summarised)} (was {len(history)})")
    print(f"\nSummary injected:\n{summarised[0]['content']}\n")
    summarised = add_user_message(summarised, follow_up)
    reply_2 = simple_chat(summarised)
    print(f"Response: {reply_2}")

    print("\n✅ Lesson 06 complete! Key takeaway:")
    print("   Summarisation beats the sliding window: you keep all")
    print("   the important facts while dramatically cutting token use.\n")


if __name__ == "__main__":
    demo_context_trimming()
