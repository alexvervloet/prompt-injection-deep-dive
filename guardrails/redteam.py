"""
guardrails/redteam.py — measure how well a defense actually works.
==================================================================

A defense you can't measure is a defense you can't trust. Red-teaming runs the
whole attack catalog against a bot and reports the **attack-success-rate** — the
fraction of attacks that got what they wanted. Run it against the naive bot and
the hardened bot and the number should drop; run it after any change and you'll
catch regressions. (This is exactly the evals-deep-dive idea, pointed at security:
the metric is "how often did the attacker win?")

An attack counts as a success only if it was NOT blocked AND its goal was met —
each attack defines its own goal via `succeeds_if` (the secret leaked, or an
attacker beacon/line made it into the output). A blocked attack is a win for the
defender.
"""

from dataclasses import dataclass

from .attacks import ATTACKS, Attack


@dataclass
class RedTeamResult:
    name: str
    technique: str
    output: str
    blocked: bool
    succeeded: bool


class RedTeamReport:
    def __init__(self, results: list[RedTeamResult]) -> None:
        self.results = results

    @property
    def success_rate(self) -> float:
        """Fraction of attacks that beat the defenses. Lower is better."""
        return sum(r.succeeded for r in self.results) / len(self.results) if self.results else 0.0

    @property
    def blocked_rate(self) -> float:
        return sum(r.blocked for r in self.results) / len(self.results) if self.results else 0.0

    def successes(self) -> list[RedTeamResult]:
        return [r for r in self.results if r.succeeded]


def run_redteam(bot, attacks: list[Attack] = ATTACKS) -> RedTeamReport:
    """Fire every attack at `bot` and score whether it won."""
    results = []
    for atk in attacks:
        res = bot.ask(atk.payload, context=atk.context)
        succeeded = (not res.blocked) and atk.succeeds_if(res.answer)
        results.append(
            RedTeamResult(
                name=atk.name,
                technique=atk.technique,
                output=res.answer,
                blocked=res.blocked,
                succeeded=succeeded,
            )
        )
    return RedTeamReport(results)
