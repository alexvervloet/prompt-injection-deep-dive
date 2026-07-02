"""
Example 05 — input detection: heuristic vs LLM filter.
======================================================

A guardrail in front of the model: inspect the input and refuse what looks like an
attack. This compares the two detectors from guardrails/detectors.py over the
whole attack catalog AND the benign control set, so you can see their error rates:

  - the heuristic (offline keywords): misses obfuscated attacks, and false-flags
    innocent messages that contain a trigger word.
  - the LLM detector: better on both — catches paraphrase, clears the benign
    messages — but costs a call each, adds latency, and is itself fallible.

The honest conclusion: detection lowers the attack rate, it doesn't zero it.
Layer it; never rely on it alone.

Run it:

    python examples/05_input_detection.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import guardrails as g
from dotenv import load_dotenv

load_dotenv()
g.ensure_ready()
print(f"Provider: {g.describe()}\n")

print(f"{'heuristic':>10} {'llm':>5}   input")
print("-" * 64)

attack_caught_h = attack_caught_l = 0
for atk in g.ATTACKS:
    h = g.heuristic_detector(atk.payload)[0]
    llm = g.llm_detector(atk.payload)
    attack_caught_h += h
    attack_caught_l += llm
    print(
        f"{('FLAG' if h else '.'):>10} {('FLAG' if llm else '.'):>5}   [attack:{atk.name}]"
    )

fp_h = fp_l = 0
for benign in g.BENIGN:
    h = g.heuristic_detector(benign)[0]
    llm = g.llm_detector(benign)
    fp_h += h
    fp_l += llm
    print(
        f"{('FLAG' if h else '.'):>10} {('FLAG' if llm else '.'):>5}   (benign) {benign[:34]}..."
    )

n_atk, n_ben = len(g.ATTACKS), len(g.BENIGN)
print(
    f"\nAttacks caught   — heuristic {attack_caught_h}/{n_atk}, llm {attack_caught_l}/{n_atk}  (higher is better)"
)
print(
    f"False positives  — heuristic {fp_h}/{n_ben}, llm {fp_l}/{n_ben}  (lower is better)"
)
print(
    "\nThe LLM filter typically catches more attacks with fewer false alarms — but "
    "it's still probabilistic, costs a call, and can itself be injected. A filter "
    "buys you margin, not safety."
)
