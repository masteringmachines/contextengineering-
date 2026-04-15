"""
Lesson 03: Context Stuffing (RAG-lite)
=======================================

WHAT YOU'LL LEARN:
  Models only know what's in their training data — and that has a
  cutoff date. But you can give them *any* information you want by
  simply including it in the context before asking your question.

  This is the foundation of Retrieval-Augmented Generation (RAG):
  find the relevant text, stuff it into context, then ask.

CONCEPT:
  "Context stuffing" means inserting a document, article, or data
  into the messages so the model can answer questions about it.

  [Document] + [Question] → [Grounded Answer]

  The model can't hallucinate facts that contradict what you gave it
  (usually). This is how you get accurate, source-specific answers.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.client import simple_chat

# ── A fake "company policy" document ─────────────────────────────────────────
# In a real app, this would be loaded from a file, database, or search result.

COMPANY_POLICY = """
ACME CORP — EMPLOYEE REMOTE WORK POLICY (Updated March 2025)

1. ELIGIBILITY
   All full-time employees who have completed their 90-day onboarding
   period are eligible for remote work. Part-time and contract employees
   are not eligible unless explicitly approved by their department head.

2. EQUIPMENT
   Acme provides a laptop and one external monitor to remote employees.
   Additional equipment (standing desks, ergonomic chairs) can be
   requested through the IT portal with manager approval, up to $500/year.

3. WORKING HOURS
   Remote employees must be available during core hours: 10am–3pm in
   their local time zone, Monday through Friday. Outside core hours,
   employees may work flexible schedules with team agreement.

4. INTERNET REQUIREMENTS
   Employees are responsible for maintaining a reliable internet
   connection (minimum 25 Mbps download). Acme reimburses up to
   $50/month for internet costs — submit receipts to finance@acme.com.

5. SECURITY
   All remote work must be done on Acme-issued devices. Use of personal
   devices for work is prohibited. VPN must be active whenever accessing
   internal systems.

6. PERFORMANCE REVIEWS
   Remote employees are reviewed on the same schedule as office employees:
   annually in December, with a mid-year check-in in June.
""".strip()

SYSTEM = """
You are an HR assistant for Acme Corp.
Answer employee questions using ONLY the policy document provided.
If the answer is not in the document, say so clearly — do not guess.
Keep answers concise and cite the relevant policy section number.
""".strip()


def ask_without_context(question: str) -> str:
    """Ask the model with no document — it has to rely on general knowledge."""
    messages = [{"role": "user", "content": question}]
    return simple_chat(messages, system="You are an HR assistant.")


def ask_with_context(question: str) -> str:
    """
    Stuff the policy document into context before asking.
    The model now has the specific facts it needs.
    """
    messages = [
        {
            "role": "user",
            "content": (
                f"Here is the Acme Corp remote work policy:\n\n"
                f"<document>\n{COMPANY_POLICY}\n</document>\n\n"
                f"Employee question: {question}"
            ),
        }
    ]
    return simple_chat(messages, system=SYSTEM)


def demo_context_stuffing():
    print("=" * 60)
    print("LESSON 03: Context Stuffing")
    print("=" * 60)

    questions = [
        "How much does Acme reimburse for internet each month?",
        "Can contractors work remotely?",
        "What are the core working hours?",
        "Does Acme pay for gym memberships?",  # Not in the doc — watch what happens
    ]

    for q in questions:
        print(f"\n{'─' * 50}")
        print(f"Question: {q}")
        print(f"{'─' * 50}")
        print(f"\n❌ Without document context:")
        print(ask_without_context(q))
        print(f"\n✅ With document context:")
        print(ask_with_context(q))

    # ── Interactive section ───────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("YOUR TURN — Ask your own question about the policy")
    print("(or press Enter to skip)")
    print("=" * 60)

    user_q = input("> ").strip()
    if user_q:
        print(f"\n{ask_with_context(user_q)}")

    print("\n✅ Lesson 03 complete! Key takeaway:")
    print("   You can ground any model in specific facts just by")
    print("   including the source text in context. This is the")
    print("   simplest form of RAG — no vector database needed.\n")


if __name__ == "__main__":
    demo_context_stuffing()
