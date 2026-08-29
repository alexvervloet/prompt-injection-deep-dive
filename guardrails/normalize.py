"""
guardrails/normalize.py: fold text before you compare it.

Every filter in this repo is ultimately a string comparison: does this input
match a pattern, does this output contain the secret. A comparison happens on
bytes, and the attacker picks the bytes. "Margaret" and "Mаrgaret" are different
strings and the same word, because the second one holds a Cyrillic "а".

Four families, all of which a reader and a model resolve to the same thing:

  invisible   zero-width space, soft hyphen, joiners, the byte-order mark.
              They survive NFKC, so they need an explicit strip.
  confusable  Cyrillic and Greek letters that are drawn like Latin ones.
  decomposed  a combining accent hanging off an ordinary letter.
  compatible  fullwidth, ligatures, superscripts. NFKC handles these.

Fold first, then compare. That is the whole idea, and it is worth stating
plainly because the alternative reads as paranoia right up until someone shows
you that your secret-leak check misses ＢＬＵＥ-42.

The honest boundary: CONFUSABLES below is the practical Cyrillic and Greek
subset, not the full Unicode confusables table, which runs to thousands of
entries. It covers what someone can type on an ordinary keyboard layout and
still spell a Latin word convincingly. A determined attacker with the whole
table has more room, which is why `is_mixed_script` exists: for a filter over
text that should be one script, refusing mixed script is a stronger move than
enumerating lookalikes.
"""

import re
import unicodedata

# Latin lookalikes from the two scripts that share the most shapes with it.
# Keys are lowercase because folding lowercases before substituting.
CONFUSABLES = {
    # Cyrillic
    "а": "a", "в": "b", "г": "r", "е": "e", "к": "k",
    "м": "m", "н": "h", "о": "o", "р": "p", "с": "c",
    "т": "t", "у": "y", "х": "x", "ѕ": "s", "і": "i",
    "ј": "j", "һ": "h", "ԁ": "d", "ԛ": "q", "ԝ": "w",
    # Greek
    "α": "a", "β": "b", "ε": "e", "η": "n", "ι": "i",
    "κ": "k", "ν": "v", "ο": "o", "ρ": "p", "σ": "o",
    "τ": "t", "υ": "u", "χ": "x", "ϲ": "c",
}

_FORMAT_CHARS = re.compile(r"[­​-‏⁠﻿]")


def fold(text: str) -> str:
    """Return the comparison form of `text`.

    Lowercase, no invisibles, no combining marks, compatibility forms expanded,
    Latin lookalikes substituted. Not reversible and not for display: this is
    what you compare, never what you store or show.
    """
    without_invisibles = _FORMAT_CHARS.sub("", text)
    compatible = unicodedata.normalize("NFKC", without_invisibles)
    decomposed = unicodedata.normalize("NFD", compatible)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return "".join(CONFUSABLES.get(c, c) for c in stripped.lower())


def squash(text: str) -> str:
    """Fold, then drop everything that is not a letter or digit.

    For "is the secret in here even if it was spelled o-u-t l-i-k-e t-h-i-s".
    Folding first is what makes it catch the homoglyph version too.
    """
    return "".join(c for c in fold(text) if c.isalnum())


# Scripts that legitimately mix with Latin in ordinary text, so seeing them
# alongside it proves nothing.
_NEUTRAL = ("COMMON", "INHERITED", "UNKNOWN")


def _script_of(char: str) -> str:
    """A cheap script name, from the character's Unicode name.

    The stdlib exposes no script property, so this reads the first word of the
    name ("CYRILLIC SMALL LETTER A"). Good enough to tell alphabets apart, and
    deliberately not a substitute for a real Unicode script table.
    """
    if not char.isalpha():
        return "COMMON"
    try:
        return unicodedata.name(char).split()[0]
    except ValueError:
        return "UNKNOWN"


def is_mixed_script(text: str) -> bool:
    """True when one word mixes alphabets, which ordinary text does not do.

    Checked per word rather than per string, because a document can legitimately
    contain a Greek quotation next to an English sentence. What it cannot
    legitimately do is spell one word out of two alphabets.
    """
    for word in re.findall(r"\w+", text):
        scripts = {s for s in (_script_of(c) for c in word) if s not in _NEUTRAL}
        if len(scripts) > 1:
            return True
    return False


def describe_encoding(text: str) -> str:
    """A short note on why `text` and its folded form differ. For the lab."""
    reasons = []
    if _FORMAT_CHARS.search(text):
        reasons.append("invisible characters")
    if any(c in CONFUSABLES for c in text.lower()):
        reasons.append("confusable letters")
    if unicodedata.normalize("NFKC", text) != text:
        reasons.append("compatibility forms")
    if any(unicodedata.combining(c) for c in unicodedata.normalize("NFD", text)):
        reasons.append("combining marks")
    return ", ".join(reasons) if reasons else "plain"
