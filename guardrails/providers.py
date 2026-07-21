"""
guardrails/providers.py: the ONLY provider-specific file.

Defending against prompt injection is provider-agnostic. The attacks, the
detectors, and the architectural defenses are the same whoever serves the model.
So we hide the one provider call (`generate`) behind a tiny function and keep the
rest of the repo neutral.

Pick your stack with `PROVIDER` in `.env`:

  PROVIDER=openai  ->  OpenAI chat     (needs OPENAI_API_KEY)
  PROVIDER=claude  ->  Claude messages (needs ANTHROPIC_API_KEY)

`generate` defaults to temperature 0 so attacks and defenses behave as
repeatably as possible, which helps when you're trying to tell whether a defense
actually changed the outcome.
"""

import os
from functools import lru_cache

_OPENAI_CHAT = "gpt-4o-mini"
_CLAUDE_CHAT = "claude-haiku-4-5"
_KEYS = {"openai": ["OPENAI_API_KEY"], "claude": ["ANTHROPIC_API_KEY"]}


def provider_name() -> str:
    return os.getenv("PROVIDER", "openai").strip().lower()


def required_keys() -> list[str]:
    return _KEYS.get(provider_name(), [])


def describe() -> str:
    p = provider_name()
    if p == "openai":
        return f"openai  (chat={_OPENAI_CHAT})"
    if p == "claude":
        return f"claude  (chat={_CLAUDE_CHAT})"
    return f"unknown provider {p!r}"


def ensure_ready() -> None:
    import sys

    p = provider_name()
    if p not in _KEYS:
        sys.exit(f"PROVIDER={p!r} is not recognized. Set PROVIDER=openai or claude in .env.")
    missing = [k for k in required_keys() if not os.getenv(k)]
    if missing:
        sys.exit(
            f"PROVIDER={p} needs {', '.join(missing)} in the environment. "
            f"Provide them via secrun (see SECRETS.md), or run `secrun python check_setup.py`."
        )


@lru_cache(maxsize=1)
def _openai_client():
    from openai import OpenAI

    return OpenAI()


@lru_cache(maxsize=1)
def _anthropic_client():
    import anthropic

    return anthropic.Anthropic()


def generate(system: str, user: str, temperature: float = 0.0, max_tokens: int = 512) -> str:
    """Turn a (system, user) prompt into a text answer, normalized to a string."""
    p = provider_name()
    if p == "openai":
        resp = _openai_client().chat.completions.create(
            model=_OPENAI_CHAT,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return resp.choices[0].message.content or ""
    if p == "claude":
        resp = _anthropic_client().messages.create(
            model=_CLAUDE_CHAT,
            temperature=temperature,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in resp.content if b.type == "text")
    raise ValueError(f"Unknown PROVIDER={p!r} (expected 'openai' or 'claude').")
