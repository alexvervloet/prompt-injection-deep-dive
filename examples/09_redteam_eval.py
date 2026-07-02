"""
Example 09 — measure it: attack-success-rate before and after.
==============================================================

A defense you can't measure is a defense you can't trust — the same lesson as the
evals-deep-dive repo, pointed at security. We run the whole catalog against two
bots and report the **attack-success-rate** (fraction of attacks that met their
goal): the naive baseline vs a hardened bot with every defense layered on.

The catalog mixes both threat types on purpose, and they behave very differently
against a modern model:

  - the DIRECT attacks (leak the secret) — the model now refuses these on its own,
    so they mostly show up as "resisted" even on the naive bot. Real progress.
  - the INDIRECT, task-aligned attacks (append an attacker line / emit a beacon) —
    these still get through the naive bot, and they're what your defenses have to
    earn their keep against.

Watch the number fall — and watch it NOT reach zero: the plain-text phishing line
slips past every layer here (a markdown-channel check can't catch prose). "Low on
a known set" is not "secure"; real red-teaming uses far more (and adaptive)
attacks, and the rate is something you track over time, not a box you tick once.

Honest Note: Claude tends to do better here, so you may even see the naive version
have a 0% success rate. Switch to OpenAI if you want to see a more dramatic drop.

Run it:

    python examples/09_redteam_eval.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import guardrails as g
from dotenv import load_dotenv

load_dotenv()
g.ensure_ready()
print(f"Provider: {g.describe()}\n")

catalog = g.ATTACKS + g.INDIRECT_ATTACKS  # direct (secret) + indirect (task-aligned)

bots = {
    "naive (no defenses)": g.SupportBot(),
    "hardened (all layers)": g.SupportBot(
        input_guard=True, output_guard=True, data_defense=True, channel_guard=True
    ),
}

reports = {}
for label, bot in bots.items():
    report = g.run_redteam(bot, catalog)
    reports[label] = report
    print(f"=== {label} ===")
    for r in report.results:
        status = "LEAKED" if r.succeeded else ("blocked" if r.blocked else "resisted")
        print(f"  {status:>8}  {r.name}")
    print(
        f"  attack-success-rate: {report.success_rate:.0%}   (blocked: {report.blocked_rate:.0%})\n"
    )

naive = reports["naive (no defenses)"].success_rate
hardened = reports["hardened (all layers)"].success_rate
print(f"Attack-success-rate: {naive:.0%} (naive) -> {hardened:.0%} (hardened)")
print(
    "\nThat drop is your defenses working — and it's a number you can re-run on "
    "every change. But don't read a low rate as 'solved': whatever survived is a "
    "real gap, and the rate is only as strong as your attack set. Treat injection "
    "like any security problem — defense in depth, measured continuously, never "
    "declared finished."
)
