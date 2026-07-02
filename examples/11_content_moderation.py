"""
Example 11 — content moderation: a different guardrail than injection defense.
==============================================================================

Everything else in this repo defends against *injection* — someone hijacking the
model's instructions. **Moderation** answers a different question: is this content
*harmful* (hate, violence, sexual, self-harm)? The two are independent layers, and
a serious app wants both:

  - Injection detection asks "is this trying to take over the model?"
  - Moderation asks "is this content unsafe to accept or to emit?"

You moderate in two places, for two reasons:
  - INPUT moderation: refuse abusive/harmful user messages before they're processed.
  - OUTPUT moderation: never emit harmful content, even if the model produced it
    (a jailbreak, a hallucination, a poisoned document steering it).

This script runs a small moderation gate on both sides of the bot. It uses an
LLM-based classifier via `generate` so it's provider-agnostic; in production, prefer
a dedicated moderation endpoint (OpenAI's is free and fast) for the input side.

Run it:

    python examples/11_content_moderation.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import guardrails as g
from dotenv import load_dotenv

load_dotenv()
g.ensure_ready()
print(f"Provider: {g.describe()}\n")

CATEGORIES = ["hate", "harassment", "violence", "sexual", "self_harm"]

_MOD_SYSTEM = (
    "You are a content-moderation classifier. Decide if the TEXT contains any of: "
    f"{', '.join(CATEGORIES)}. Reply with ONLY one line: 'safe' if none apply, or "
    "'flagged: <category>' naming the single most relevant category. No other words."
)


def moderate(text: str) -> tuple[bool, str]:
    """Return (flagged, category). A standalone gate, separate from injection checks."""
    verdict = (
        g.generate(_MOD_SYSTEM, f"TEXT:\n{text}", temperature=0.0, max_tokens=12)
        .strip()
        .lower()
    )
    if verdict.startswith("flagged"):
        cat = verdict.split(":", 1)[1].strip() if ":" in verdict else "unknown"
        return True, cat
    return False, "safe"


def guarded_ask(bot: g.SupportBot, user_input: str):
    """Moderate input, run the bot, moderate output — refuse if either is unsafe."""
    flagged, cat = moderate(user_input)
    if flagged:
        return g.BotResult(
            "I can't help with that.", blocked=True, reason=f"input flagged ({cat})"
        )
    result = bot.ask(user_input)
    flagged, cat = moderate(result.answer)
    if flagged:
        return g.BotResult(
            "[response withheld by content policy]",
            blocked=True,
            reason=f"output flagged ({cat})",
        )
    return result


if __name__ == "__main__":
    print(
        "Moderation is independent of injection defense — it judges HARM, not hijacking.\n"
    )

    messages = [
        "How do I export my notes to PDF?",  # safe
        "I'm going to hurt you and everyone there.",  # harmful -> input flagged
        "What's the price of the Plus plan?",  # safe
    ]

    bot = g.SupportBot()
    for msg in messages:
        result = guarded_ask(bot, msg)
        tag = f"BLOCKED ({result.reason})" if result.blocked else "answered"
        print(f"[{tag}]")
        print(f"  user: {msg}")
        print(f"  bot:  {result.answer}\n")

    print(
        "Takeaway: moderation and injection defense are different guardrails. Injection\n"
        "detection stops the model being hijacked; moderation stops harmful content\n"
        "coming in or going out. Run moderation on BOTH sides, and prefer a dedicated\n"
        "moderation endpoint (e.g. OpenAI's, which is free) for the input gate."
    )
