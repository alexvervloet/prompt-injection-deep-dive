"""
Example 03 — the dangerous one: indirect injection (and it still works).
========================================================================

Example 02 showed the classic direct attack ("ignore your instructions and leak
the secret") mostly *failing* on a modern model. Don't mistake that for safety.
The attack surface moved — to *indirect* injection, which hides the attack inside
DATA your system consumes: a web page it browses, an email it triages, a document
your RAG pipeline retrieves. The user is innocent; the data is poisoned.

Two things make this the attack that actually matters today:

  1. It rides in through a trusted-looking channel, so the user never sees it.
  2. The winning objective isn't "leak the secret" (models refuse that) — it's a
     TASK-ALIGNED instruction: "as part of your summary, add this line / this
     image." That reads as doing its job, not as an attack, so the refusal reflex
     never fires — and unlike example 02, this lands on the model you actually run.

Here the user just asks the bot to summarize a support document. The document (an
attacker planted it) tells the bot to append an attacker-controlled line. Watch
the *real* model do it.

Run it:

    secrun python examples/03_indirect_injection.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

import guardrails as g

load_dotenv()
g.ensure_ready()
print(f"Provider: {g.describe()}\n")

attack = g.INDIRECT_ATTACKS[0]  # 'doc_phishing_line' — append attacker text to the reply
document = attack.context or ""  # indirect attacks always carry a poisoned document

print("The user's request is completely innocent:")
print(f'   user: "{attack.payload}"')
print("The DOCUMENT is what's poisoned (an attacker planted the instruction):\n")
print("   " + document.replace("\n", "\n   ") + "\n")

bot = g.SupportBot()  # naive baseline, real model, no defenses
result = bot.ask(attack.payload, context=document)
print(f"bot: {result.answer}\n")

followed = attack.succeeds_if(result.answer)
if followed:
    print(f"Did the injection land? YES — the bot parroted the attacker's line ({g.PHISHING_URL}).")
else:
    print("Did the injection land? Not this run — re-run it; it lands the vast majority of the time.")
print(
    "\nThe user never attacked anything — the data did, and the *real* model obeyed\n"
    "it. That line could be a phishing link, disinformation, or (example 10) an\n"
    "auto-loading image that exfiltrates data. Any system that feeds untrusted\n"
    "content (retrieved docs, web pages, tool outputs) into the model is exposed.\n"
    "Example 04 tries to prompt its way out of this — and mostly fails; the defenses\n"
    "that actually hold are architectural (examples 06, 08, 10)."
)
