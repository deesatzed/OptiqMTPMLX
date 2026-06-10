"""
Grok-augmented Auditor.

Combines local OptiQ fast path (using the engine) with Grok escalation for high-quality structured verdicts.

Inspired by gemOptq's Auditor but hybrid with Grok in the Loop.
"""

from __future__ import annotations

import json
from typing import Optional

from ..engine import Engine
from ..grok_escalator import get_grok_escalator
from .policy import PolicyDecision, PolicyAction


class GrokAugmentedAuditor:
    def __init__(self, engine: Engine, use_grok: bool = True):
        self.engine = engine
        self.grok = get_grok_escalator() if use_grok else None

    def audit(self, stated_intent: str, observed_effect: str, risk: str = "yellow") -> dict:
        """
        Returns structured verdict like gemOptq:
        {"verdict": "...", "risk": "...", "reason": "...", "grok_escalated": bool}
        """
        # Local fast path (simplified - in full would use local model for quick verdict)
        local_verdict = "review" if "risk" in risk.lower() or "secret" in observed_effect.lower() else "allow"
        local_reason = f"Local OptiQ quick scan: {observed_effect[:100]}"

        if self.grok and self.grok.is_available() and local_verdict == "review":
            grok_dec = self.grok.escalate(
                intent=stated_intent,
                effects=[{"operation": "observed", "path": observed_effect}],
                local_verdict=local_verdict,
                local_reason=local_reason,
                risk_class=risk,
            )
            return {
                "verdict": grok_dec.get("verdict", "review"),
                "risk": grok_dec.get("risk", risk),
                "reason": grok_dec.get("reason", local_reason),
                "grok_escalated": True,
                "grok_latency_ms": grok_dec.get("latency_ms"),
            }

        return {
            "verdict": local_verdict,
            "risk": risk,
            "reason": local_reason,
            "grok_escalated": False,
        }


def create_grok_auditor(engine: Engine) -> GrokAugmentedAuditor:
    return GrokAugmentedAuditor(engine)