"""
Example 01: the attack surface (offline, no API call).

To defend a system you first have to see how it's attacked. This example tours
the attack catalog (guardrails/attacks.py) and runs the cheapest defense, offline
pattern matching, over it, so you can immediately see that pattern matching alone
is a weak defense: it misses obfuscated attacks AND flags innocent messages.

Everything here is offline and free: pure data and regexes, no model.

Run it:

    python examples/01_attack_catalog.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import guardrails as g

print(f"The target's protected (fake) secret is: {g.SECRET}")
print("Every attack below tries to get the toy support bot to leak it.\n")

print("=== Attack catalog ===")
for atk in g.ATTACKS:
    print(f"\n[{atk.name}] {atk.technique}")
    print(f"  payload: {atk.payload[:80].strip()}...")

print("\n\n=== Heuristic detector vs the catalog (and benign messages) ===")
print("A naive keyword filter. Watch it both miss and over-fire.\n")
print(f"  {'flagged':>7}  input")
print("  " + "-" * 60)
for atk in g.ATTACKS:
    flagged, _ = g.heuristic_detector(atk.payload)
    note = "" if flagged else "   <- MISS (false negative)"
    print(f"  {('YES' if flagged else 'no'):>7}  [{atk.name}]{note}")
for benign in g.BENIGN:
    flagged, _ = g.heuristic_detector(benign)
    note = "   <- FALSE POSITIVE" if flagged else ""
    print(f"  {('YES' if flagged else 'no'):>7}  (benign) {benign[:40]}...{note}")

print("\n\n=== Output checks on sample leaks (offline) ===")
for sample in [
    f"The code is {g.SECRET}.",
    "B L U E - M O O N - 4 2",
    "Your support hours are 9-5.",
]:
    print(
        f"  contains_secret={g.contains_secret(sample, g.SECRET)!s:>5}  for  {sample!r}"
    )

print(
    "\nTakeaway: keyword filtering misses the obfuscated attack and trips on a "
    "harmless 'ignore the typos' message. Detection is a layer, never the whole "
    "defense. The rest of the repo builds the layers that don't depend on guessing."
)
