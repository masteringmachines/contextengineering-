# Context Engineering for Beginners 🧠

A hands-on Python project for learning **context engineering** — the practice of deliberately designing what information you give an AI model, and how you structure it, to get dramatically better results.

> **"Prompt engineering is writing a good sentence. Context engineering is designing the whole page."**

---

## What Is Context Engineering?

When you talk to an AI model, everything it can "see" in that conversation is called the **context window**. Context engineering is the skill of intentionally choosing and structuring what goes into that window:

- What instructions does the model have?
- What examples have you shown it?
- What facts or documents did you include?
- What has it already said (conversation history)?
- What tools or memory does it have access to?

Small changes to context can turn a frustrating, generic response into something genuinely useful. This project teaches you how, hands-on, with real code.

---

## What You'll Learn

| Lesson | Concept | What You'll Build |
|--------|---------|-------------------|
| 01 | System prompts | A customer support bot with a defined persona |
| 02 | Few-shot examples | A classifier that learns from examples, not instructions |
| 03 | Context stuffing | A Q&A bot that reads a document before answering |
| 04 | Conversation history | A multi-turn assistant that remembers what was said |
| 05 | Structured output | A model that always returns clean, parseable JSON |
| 06 | Context limits & trimming | Handling long conversations without hitting token limits |
| 07 | Putting it together | A mini "personal research assistant" using all techniques |

---

## Prerequisites

- Python 3.9+
- An Anthropic API key ([get one here](https://console.anthropic.com/))
- Basic Python knowledge (functions, loops, dictionaries)

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/context-engineering-intro.git
cd context-engineering-intro

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
cp .env.example .env
# Open .env and add your key: ANTHROPIC_API_KEY=sk-ant-...

# 5. Run your first lesson
python examples/01_system_prompts.py
```

---

## Project Structure

```
context-engineering-intro/
│
├── README.md                   ← You are here
├── requirements.txt            ← Dependencies
├── .env.example                ← API key template
│
├── examples/                   ← One file per lesson, fully runnable
│   ├── 01_system_prompts.py
│   ├── 02_few_shot.py
│   ├── 03_context_stuffing.py
│   ├── 04_conversation_history.py
│   ├── 05_structured_output.py
│   ├── 06_context_trimming.py
│   └── 07_research_assistant.py
│
├── system_prompts/             ← Reusable system prompt templates
│   ├── support_agent.txt
│   ├── research_assistant.txt
│   └── json_extractor.txt
│
├── utils/
│   ├── client.py               ← Shared Anthropic client setup
│   ├── history.py              ← Conversation history helpers
│   └── tokens.py               ← Token counting utilities
│
└── notebooks/                  ← Jupyter versions of each lesson
    └── context_engineering_walkthrough.ipynb
```

---

## Key Concepts Explained

### The Context Window
Every API call is stateless — the model remembers nothing between calls. You must manually include everything it needs to know. The context window is the total amount of text (measured in **tokens**) the model can process at once.

### Tokens
Tokens are chunks of text, roughly 3–4 characters each. `claude-sonnet-4-5` has a 200,000 token context window — about 150,000 words. You pay per token, so context engineering is also about being precise.

### The Messages Array
Every call to the API uses a `messages` list. Each message has a `role` (`user` or `assistant`) and `content`. The order matters — the model reads it top to bottom, just like a conversation.

```python
messages = [
    {"role": "user", "content": "What is the capital of France?"},
    {"role": "assistant", "content": "Paris."},
    {"role": "user", "content": "And what's its population?"},
]
```

---

## Running the Final Project

```bash
python examples/07_research_assistant.py
```

This launches an interactive research assistant that:
- Holds a full conversation with you
- Accepts a document or URL you paste in
- Answers questions about it
- Summarizes what it has learned
- Trims old context automatically when the conversation gets long

---

## Resources

- [Anthropic API Docs](https://docs.anthropic.com)
- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
- [Context Window Explainer](https://www.anthropic.com/news/claude-3-7-sonnet)

---

## Contributing

Found a bug or want to add a lesson? Open an issue or PR — beginner-friendly contributions especially welcome.

---

## License

MIT
