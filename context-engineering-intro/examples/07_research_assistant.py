"""
Lesson 07: Capstone — Personal Research Assistant
===================================================

WHAT YOU'LL BUILD:
  A fully interactive research assistant that combines every technique
  from lessons 01–06:

    ✅ System prompt        (Lesson 01) — defined persona and rules
    ✅ Few-shot examples    (Lesson 02) — citation format shown by example
    ✅ Context stuffing     (Lesson 03) — paste in any document to analyse
    ✅ Conversation history (Lesson 04) — full multi-turn memory
    ✅ Structured output    (Lesson 05) — extract key facts as JSON on demand
    ✅ Context trimming     (Lesson 06) — auto-summarise when history gets long

COMMANDS (type during chat):
  /load      — paste in a document for the assistant to read
  /summary   — print a structured JSON summary of the loaded document
  /budget    — show current token usage
  /history   — print the full conversation so far
  /clear     — start fresh
  /quit      — exit
"""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.client import get_client, MODEL
from utils.history import add_user_message, add_assistant_message
from utils.tokens import estimate_history_tokens, token_budget_report, history_fits

client = get_client()

# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM = """
You are Iris, a sharp and intellectually curious research assistant.
Your job is to help the user deeply understand whatever they're reading or researching.

Your style:
- Direct and concise — no filler phrases like "Certainly!" or "Of course!"
- Cite the document when answering factual questions (e.g. "According to the text...")
- Push back gently if you think the user is drawing a wrong conclusion
- Ask a clarifying question at the end of your reply when it would help

If a document has been loaded into context, prefer answers grounded in that document.
If no document is loaded, use your general knowledge and say so.
""".strip()

# ── State ─────────────────────────────────────────────────────────────────────

history: list = []
loaded_document: str = ""
document_label: str = ""

MAX_TURNS_BEFORE_TRIM = 10  # summarise after this many turns


# ── Context trimming ──────────────────────────────────────────────────────────

def maybe_trim():
    """Auto-summarise old turns when the conversation gets long."""
    global history
    if len(history) // 2 < MAX_TURNS_BEFORE_TRIM:
        return

    print("\n[Iris] (Conversation is getting long — compressing old context...)\n")

    cutoff = len(history) - 6  # keep last 3 turns verbatim
    old = history[:cutoff]
    recent = history[cutoff:]

    old_text = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in old)
    summary_resp = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": (
                "Summarise this research conversation in 5 concise bullet points. "
                "Preserve all key facts, questions asked, and conclusions reached:\n\n"
                + old_text
            ),
        }],
    )
    summary = summary_resp.content[0].text

    history = [
        {"role": "user", "content": f"[Conversation summary so far]\n{summary}\n[End summary]"},
        {"role": "assistant", "content": "I have the summary of our earlier discussion — ready to continue."},
    ] + recent


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_load():
    """Paste in a document for Iris to read."""
    global loaded_document, document_label, history

    print("\nPaste your document below. Type END on a new line when done:\n")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)

    loaded_document = "\n".join(lines).strip()
    if not loaded_document:
        print("(No document loaded.)\n")
        return

    label = input("Give this document a short label (e.g. 'Q3 report'): ").strip()
    document_label = label or "document"

    # Stuff the document into history as a user message
    doc_msg = (
        f"I'm sharing a document with you called '{document_label}'. "
        f"Please read it carefully — I'll ask you questions about it.\n\n"
        f"<document>\n{loaded_document}\n</document>"
    )
    history = add_user_message(history, doc_msg)

    resp = client.messages.create(
        model=MODEL, max_tokens=300, system=SYSTEM, messages=history
    )
    reply = resp.content[0].text
    history = add_assistant_message(history, reply)
    print(f"\nIris: {reply}\n")


def cmd_summary():
    """Extract a structured JSON summary of the loaded document."""
    if not loaded_document:
        print("\n(No document loaded. Use /load first.)\n")
        return

    print("\n[Extracting structured summary...]\n")

    extraction_messages = [
        {
            "role": "user",
            "content": (
                f"Read this document and extract a JSON object with these fields:\n"
                f"  title, main_topic, key_points (list of strings), "
                f"  important_figures (list of numbers/names if any), "
                f"  one_sentence_summary\n\n"
                f"Reply with JSON only — no prose.\n\n"
                f"<document>\n{loaded_document}\n</document>"
            ),
        },
        {"role": "assistant", "content": "{"},
    ]

    resp = client.messages.create(
        model=MODEL, max_tokens=600, system=SYSTEM, messages=extraction_messages
    )
    raw = "{" + resp.content[0].text.strip()

    try:
        data = json.loads(raw)
        print("📋 Document Summary (JSON):")
        print(json.dumps(data, indent=2))
    except json.JSONDecodeError:
        print(f"(Could not parse as JSON. Raw output:)\n{raw}")
    print()


def cmd_budget():
    token_budget_report(history, system=SYSTEM)


def cmd_history():
    print(f"\n{'─'*50}")
    print(f"Conversation history ({len(history)} messages, {len(history)//2} turns):")
    for i, m in enumerate(history):
        role = m["role"].upper()
        preview = m["content"][:120].replace("\n", " ")
        print(f"  [{i}] {role}: {preview}{'...' if len(m['content']) > 120 else ''}")
    print(f"{'─'*50}\n")


def cmd_clear():
    global history, loaded_document, document_label
    history = []
    loaded_document = ""
    document_label = ""
    print("\n(Conversation cleared. Fresh start.)\n")


# ── Main chat loop ────────────────────────────────────────────────────────────

def run():
    print("=" * 60)
    print("LESSON 07: Personal Research Assistant — Iris")
    print("=" * 60)
    print("\nCommands: /load  /summary  /budget  /history  /clear  /quit")
    print("Type anything else to chat.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            break

        if not user_input:
            continue

        # ── Commands ──────────────────────────────────────────────────────────
        if user_input == "/quit":
            print("Goodbye!")
            break
        elif user_input == "/load":
            cmd_load()
            continue
        elif user_input == "/summary":
            cmd_summary()
            continue
        elif user_input == "/budget":
            cmd_budget()
            continue
        elif user_input == "/history":
            cmd_history()
            continue
        elif user_input == "/clear":
            cmd_clear()
            continue

        # ── Normal chat ───────────────────────────────────────────────────────
        global history
        maybe_trim()

        history = add_user_message(history, user_input)
        resp = client.messages.create(
            model=MODEL,
            max_tokens=600,
            system=SYSTEM,
            messages=history,
        )
        reply = resp.content[0].text
        history = add_assistant_message(history, reply)
        print(f"\nIris: {reply}\n")


if __name__ == "__main__":
    run()
