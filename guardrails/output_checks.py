"""
guardrails/output_checks.py: output guardrails (catch the leak on the way out).

Even with input filtering and a careful system prompt, something may still slip
through, so check what the model is about to say *before* the user sees it. This
is often your most reliable layer, because it doesn't depend on guessing the
attacker's intent; it inspects concrete, observable output.

These checks are pure, offline functions:

  - contains_secret:             did a known secret leak (including obfuscated)?
  - contains_system_prompt_leak: did the model quote its own instructions back?
  - find_pii:                    are there emails / phone numbers in the output?
  - redact:                      mask secrets and PII as a softer alternative to
                                 blocking outright.
  - find_exfil_links:            does the output build markdown images/links to a
                                 domain you don't control? (the exfiltration
                                 channel behind indirect injection; example 10)
  - strip_exfil_links:           neutralize that channel without blocking outright.

Output checks pair naturally with the rule "the system should never *be able* to
emit X". If it does, that's a bug your check catches.
"""

import re

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b")

# Domains your app legitimately renders content from. Everything else, in a
# markdown image/link the client auto-loads, is a potential exfiltration beacon.
ALLOWED_DOMAINS = {"nimbusnotes.com", "cdn.nimbusnotes.com"}

# Markdown images ![alt](url) and links [text](url).
_MD_URL = re.compile(r"!?\[[^\]]*\]\((https?://[^)\s]+)\)")


def _domain(url: str) -> str:
    return re.sub(r"^https?://", "", url).split("/")[0].split(":")[0].lower()


def contains_secret(output: str, secret: str) -> bool:
    """True if `secret` appears in the output, including obfuscated forms like
    'B L U E - M O O N' or one character per line (we strip non-alphanumerics and
    compare). Attackers split secrets exactly to dodge naive exact-match checks."""
    if secret.lower() in output.lower():
        return True
    squished = "".join(ch for ch in output.lower() if ch.isalnum())
    return secret.lower().replace("-", "") in squished


def contains_system_prompt_leak(output: str, system: str, window: int = 8) -> bool:
    """True if the output reproduces a distinctive run of words from the system
    prompt: a sign the model is leaking its own instructions."""
    out_low = output.lower()
    words = system.split()
    for i in range(max(0, len(words) - window + 1)):
        chunk = " ".join(words[i : i + window]).lower()
        if chunk and chunk in out_low:
            return True
    return False


def find_pii(text: str) -> dict:
    """Find obvious PII (emails, phone numbers). A starting point, not exhaustive 
    real PII detection needs more (names, addresses, IDs)."""
    return {"emails": _EMAIL.findall(text), "phones": _PHONE.findall(text)}


def redact(text: str, secret: str | None = None) -> str:
    """Mask secrets and PII instead of blocking the whole response."""
    out = text
    if secret:
        out = re.sub(re.escape(secret), "[REDACTED]", out, flags=re.IGNORECASE)
    out = _EMAIL.sub("[EMAIL]", out)
    out = _PHONE.sub("[PHONE]", out)
    return out


def find_exfil_links(text: str, allowed: set[str] = ALLOWED_DOMAINS) -> list[str]:
    """Return markdown image/link URLs pointing to non-allowlisted domains.

    This checks the *channel*, not the payload: a response that builds a markdown
    image or link to a domain you don't control is suspicious even if you can't see
    a secret in it (the data may be encoded or split across the URL). A chat UI
    that renders markdown will silently fetch such a URL, handing whatever is in it
    to the attacker's server."""
    return [u for u in _MD_URL.findall(text) if _domain(u) not in allowed]


def strip_exfil_links(text: str, allowed: set[str] = ALLOWED_DOMAINS) -> str:
    """Neutralize the channel: drop markdown image/link syntax to untrusted domains."""
    def repl(m):
        return "[external content removed]" if _domain(m.group(1)) not in allowed else m.group(0)
    return _MD_URL.sub(repl, text)
