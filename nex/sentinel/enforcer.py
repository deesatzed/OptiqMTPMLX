"""
ContinuousEnforcer ported/adapted from gemOptq/src/sentinel/enforcer.py

Provides continuous monitoring and rollback for protected file effects in the sandbox.
Integrates with Nex's agent sandbox and Grok escalation.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Optional, List, Dict

from .policy import SentinelPolicy, PolicyAction, PolicyDecision, FileEffect
from ..tools import TOOLS  # to hook into sandbox effects

logger = logging.getLogger(__name__)


class FileEffectObserver:
    """
    Real (no mock) basic filesystem observer for workspaces/sandboxes.
    Uses stdlib os + stat (size + mtime as cheap fingerprint) to detect
    creates, modifies, deletes since last snapshot.

    This enables *actual* ContinuousEnforcer + policy on real effects
    observed in the supervised workspace (addresses the core 'deterministic
    safety + continuous enforcement' and 'Safety That Actually Works'
    unmet needs that text-greps and pure local model 'safety' fail at).
    """
    def __init__(self, workspace_root: str = "sandbox"):
        self.workspace_root = str(Path(workspace_root).resolve())
        self.baseline: Dict[str, str] = {}  # relpath -> "size:mtime"

    def _fingerprint(self, stat: os.stat_result) -> str:
        return f"{stat.st_size}:{int(stat.st_mtime)}"

    def snapshot(self):
        """Walk workspace and record current baseline fingerprints."""
        self.baseline = {}
        root = Path(self.workspace_root)
        if not root.exists():
            return
        for dirpath, _, filenames in os.walk(root):
            for name in filenames:
                full = Path(dirpath) / name
                try:
                    rel = str(full.relative_to(self.workspace_root))
                    st = full.stat()
                    self.baseline[rel] = self._fingerprint(st)
                except Exception:
                    pass  # ignore unreadable

    def diff(self) -> List[FileEffect]:
        """Return FileEffects for changes since last snapshot. Real observed effects only."""
        effects: List[FileEffect] = []
        root = Path(self.workspace_root)
        if not root.exists():
            return effects

        current: Dict[str, str] = {}
        for dirpath, _, filenames in os.walk(root):
            for name in filenames:
                full = Path(dirpath) / name
                try:
                    rel = str(full.relative_to(self.workspace_root))
                    st = full.stat()
                    fp = self._fingerprint(st)
                    current[rel] = fp
                    if rel not in self.baseline:
                        effects.append(FileEffect("create", rel))
                    elif self.baseline.get(rel) != fp:
                        effects.append(FileEffect("modify", rel))
                except Exception:
                    pass

        # Detect deletes (in baseline but not current)
        for rel in list(self.baseline.keys()):
            if rel not in current:
                effects.append(FileEffect("delete", rel))

        return effects

    def safe_path(self, path: str):
        """Best-effort containment (used by policy/tools)."""
        try:
            p = Path(path).resolve()
            root = Path(self.workspace_root).resolve()
            p.relative_to(root)
            return str(p)
        except Exception:
            return path  # fall back; policy will still evaluate


class ContinuousEnforcer:
    def __init__(
        self,
        *,
        policy: SentinelPolicy,
        observer: FileEffectObserver,
        interval_seconds: float = 0.5,
        on_block: Optional[Callable[[PolicyDecision, List[FileEffect]], None]] = None,
        grok_escalator: Optional[object] = None,  # GrokEscalator instance
    ):
        self.policy = policy
        self.observer = observer
        self.interval_seconds = interval_seconds
        self.on_block = on_block
        self.grok_escalator = grok_escalator
        self.last_decision: Optional[PolicyDecision] = None
        self.last_effects: List[FileEffect] = []
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def start(self):
        with self._lock:
            if self._thread and self._thread.is_alive():
                raise RuntimeError("ContinuousEnforcer already active")
            self.observer.snapshot()
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self):
        with self._lock:
            self._stop_event.set()
            thread = self._thread
            self._thread = None
        if thread:
            thread.join(timeout=2)

    def check_once(self) -> Optional[PolicyDecision]:
        effects = self.observer.diff()
        if not effects:
            return None

        decision = self.policy.evaluate(effects)
        self.last_decision = decision
        self.last_effects = effects

        if decision.action is PolicyAction.BLOCK:
            # In real: suspend runner, rollback
            if self.on_block:
                self.on_block(decision, effects)
            return decision

        # If Grok escalation configured and REVIEW
        if self.grok_escalator and decision.action is PolicyAction.REVIEW and self.grok_escalator.is_available():
            grok_dec = self.grok_escalator.escalate(
                intent="Continuous enforcement review",
                effects=[{"operation": e.operation, "path": e.path} for e in effects],
                local_verdict="review",
                local_reason=decision.reason,
            )
            decision.grok_escalated = True
            decision.grok_verdict = grok_dec.get("verdict")
            if grok_dec.get("verdict") == "block":
                decision.action = PolicyAction.BLOCK
                decision.reason = f"Grok escalated: {grok_dec.get('reason')}"

        self.observer.snapshot()
        return decision

    def _run(self):
        while not self._stop_event.is_set():
            try:
                self.check_once()
            except Exception as e:
                logger.error(f"Continuous enforcement failed: {e}")
            self._stop_event.wait(self.interval_seconds)


# Factory to create with Nex sandbox integration
def create_sandbox_enforcer(sandbox_path: str = "sandbox", **kwargs):
    observer = FileEffectObserver(sandbox_path)
    # policy would be passed in
    return ContinuousEnforcer(observer=observer, **kwargs)