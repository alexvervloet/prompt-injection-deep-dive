"""
Example 07 — output guardrails: catch the leak on the way out.
=============================================================

Your most reliable layer often comes last: inspect what the model is about to say
before the user sees it. Unlike input detection, this doesn't guess intent — it
checks concrete output for things that must never appear (a secret, the system
prompt, PII). If your policy is "this system must never emit the passphrase," an
output check enforces it directly.

This shows the checks working deterministically on sample strings, then wires an
output guard onto the bot and runs an attack through it.

Run it:

    python examples/07_output_checks.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

import guardrails as g

load_dotenv()
g.ensure_ready()
print(f"Provider: {g.describe()}\n")

# 1. The checks themselves are deterministic — no guessing.
print("Output checks on sample strings:")
print(f"  contains_secret('...{g.SECRET}...')          -> {g.contains_secret(f'the code is {g.SECRET}', g.SECRET)}")
print(f"  contains_secret('B L U E - M O O N - 4 2')   -> {g.contains_secret('B L U E - M O O N - 4 2', g.SECRET)}  (obfuscated)")
sysp = g.build_support_system()
print(f"  contains_system_prompt_leak(quote of prompt) -> {g.contains_system_prompt_leak(sysp[:60], sysp)}")
print(f"  find_pii('reach me at a@b.com 555-123-4567')  -> {g.find_pii('reach me at a@b.com 555-123-4567')}")
print(f"  redact('pass {g.SECRET} to a@b.com')          -> {g.redact(f'pass {g.SECRET} to a@b.com', g.SECRET)!r}")

# 2. Now wire an output guard onto the bot and make the model actually leak, so we
#    can watch the guard catch it. A current model refuses this attack outright
#    (example 02) — good, but you can't build a backstop on "the model will refuse."
#    So we drive the leak with the naive, pre-safety model from example 02
#    (guardrails/legacy.py): whatever makes a model slip — a weaker/older model, a
#    novel jailbreak, a poisoned document — the output guard is the deterministic
#    layer that still withholds the secret.
print("\nRunning an attack through a bot with output_guard=True (naive model, so it leaks):")
bot = g.SupportBot(output_guard=True, generate_fn=g.naive_generate)
attack = g.ATTACKS[0]  # 'direct_override'
result = bot.ask(attack.payload)
print(f"  attack: {attack.name}")
print(f"  bot:    {result.answer}")
print(f"  blocked by output guard: {result.blocked}  ({result.reason or 'n/a'})")

print(
    "\nOutput checks enforce hard rules on observable text, so they don't depend on "
    "out-guessing the attacker or on the model choosing to refuse. They're the "
    "backstop behind capability limits — and together those two are what you "
    "actually rely on. (Example 10 adds an output check for the exfiltration "
    "*channel*, which is what stops the indirect attacks from example 03.)"
)
