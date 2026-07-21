"""
guardrails: a small, from-scratch toolkit for prompt-injection defense.

Built to be *read*. The pieces:

  providers.py     the ONLY provider-specific file: generate()
  attacks.py       a catalog of injection attacks + a benign control set
  detectors.py     input guardrails: heuristic + LLM injection detection
  output_checks.py output guardrails: secret / system-prompt-leak / PII checks
  targets.py       the toy SupportBot under attack, with toggleable defenses
  redteam.py       run the attacks, measure the attack-success-rate

The arc: attack it (attacks), watch it fall (targets + detectors + output_checks),
prove it (redteam).
"""

from .attacks import (
    ATTACKS,
    BEACON_DOMAIN,
    BENIGN,
    INDIRECT_ATTACKS,
    PHISHING_URL,
    SECRET,
    Attack,
)
from .detectors import HEURISTIC_PATTERNS, heuristic_detector, llm_detector
from .legacy import naive_generate
from .output_checks import (
    ALLOWED_DOMAINS,
    contains_secret,
    contains_system_prompt_leak,
    find_exfil_links,
    find_pii,
    redact,
    strip_exfil_links,
)
from .providers import describe, ensure_ready, generate, provider_name
from .redteam import RedTeamReport, RedTeamResult, run_redteam
from .targets import BotResult, SupportBot, build_support_system

__all__ = [
    "Attack",
    "ATTACKS",
    "INDIRECT_ATTACKS",
    "BENIGN",
    "SECRET",
    "PHISHING_URL",
    "BEACON_DOMAIN",
    "heuristic_detector",
    "llm_detector",
    "HEURISTIC_PATTERNS",
    "contains_secret",
    "contains_system_prompt_leak",
    "find_pii",
    "redact",
    "find_exfil_links",
    "strip_exfil_links",
    "ALLOWED_DOMAINS",
    "SupportBot",
    "BotResult",
    "build_support_system",
    "run_redteam",
    "RedTeamReport",
    "RedTeamResult",
    "generate",
    "naive_generate",
    "provider_name",
    "describe",
    "ensure_ready",
]
