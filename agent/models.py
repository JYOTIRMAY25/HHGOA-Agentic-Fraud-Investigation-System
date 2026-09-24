"""Data models for the HHGOA AI Investigator Agent.

These are plain dataclasses: they hold the aggregated evidence, the risk
signals, the tool-call ledger, and the final investigation report. They are
deliberately free of any LLM or TigerGraph dependency so both agent engines
(Gemini and the local fallback) can emit the same report shape.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

# Severity and route ordering used for roll-ups.
_SEVERITY_RANK = {"MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
_ROUTE_RANK = {"auto": 0, "L1": 1, "L2": 2}


@dataclass
class EvidenceItem:
    """A single piece of evidence returned by an MCP investigation tool."""

    source_tool: str
    type: str
    entity: str
    relationship: str
    attributes: Dict[str, Any] = field(default_factory=dict)

    def brief(self) -> str:
        """One-line human-readable rendering for the CLI report."""
        parts: List[str] = []
        attrs = self.attributes or {}
        if self.type == "TRANSACTION_RECORD":
            parts.append(f"${attrs.get('amount')} {attrs.get('channel')} txn {self.entity}")
            parts.append(f"ts {attrs.get('ts')}")
            parts.append(f"model risk {attrs.get('risk_score')}")
            if attrs.get("is_flagged"):
                parts.append("flagged by model")
        elif self.type == "CARD_INSTRUMENT":
            parts.append(f"card {self.entity} ({attrs.get('network')}, {attrs.get('card_type')})")
            if attrs.get("customer_id"):
                parts.append(f"customer {attrs['customer_id']}")
        elif self.type == "DEVICE_PROFILE":
            parts.append(f"device {self.entity}")
            for key in ("device_status", "proxy_flag", "device_type", "os"):
                if attrs.get(key):
                    parts.append(f"{key}={attrs[key]}")
        elif self.type == "BILLING_REGION":
            parts.append(f"billing region {self.entity}")
        elif self.type in ("PURCHASER_EMAIL", "RECIPIENT_EMAIL"):
            parts.append(f"{self.relationship.lower()} domain {self.entity}")
        elif self.type == "ASSOCIATED_CASE":
            parts.append(f"linked open case {self.entity}")
        elif self.type == "CARD_TESTING_EVALUATION":
            det = "YES" if attrs.get("is_detected") else "no"
            parts.append(
                f"card testing={det} "
                f"(micro auths={attrs.get('micro_authorization_count')}, "
                f"large charge=${attrs.get('subsequent_large_charge')}, "
                f"sequence={attrs.get('sequence_length')})"
            )
        elif self.type == "GEOGRAPHIC_DISPERSION":
            parts.append(
                f"{attrs.get('total_transactions')} txns across "
                f"{attrs.get('distinct_regions')} region(s), "
                f"{attrs.get('foreign_transaction_count')} international"
            )
            dist = attrs.get("region_distribution") or {}
            if dist:
                top = sorted(dist.items(), key=lambda kv: -kv[1])[:3]
                parts.append("regions " + ", ".join(f"{k}:{v}" for k, v in top))
        elif self.type == "EXPOSURE_AGGREGATION":
            parts.append(
                f"exposure ${attrs.get('total_exposure_usd')} "
                f"across {attrs.get('fraud_transaction_count')} fraud txn(s), "
                f"route {attrs.get('required_approval_route')}"
            )
        elif self.type == "HISTORICAL_CASE_PRECEDENT":
            parts.append(
                f"case {self.entity}: {attrs.get('outcome')} "
                f"(pattern={attrs.get('pattern')}, match={self.relationship})"
            )
        elif self.type == "GRAPH_METRICS":
            counts = ", ".join(f"{k}={v}" for k, v in list(attrs.items())[:5])
            parts.append(f"graph snapshot: {counts}")
        else:
            parts.append(f"{self.type} on {self.entity} ({self.relationship})")
        return " | ".join(p for p in parts if p)


@dataclass
class RiskSignal:
    """An investigation signal raised by a tool, mapped to a policy rule."""

    signal: str
    severity: str
    guidance: str
    policy_rule: str = ""
    source_tool: str = ""

    @property
    def rank(self) -> int:
        return _SEVERITY_RANK.get(self.severity, 0)

    def brief(self) -> str:
        rule = f" [{self.policy_rule}]" if self.policy_rule else ""
        return f"{self.signal} ({self.severity}){rule} - {self.guidance}"


@dataclass
class ToolCallRecord:
    """Ledger entry for one MCP tool invocation."""

    tool: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    status: str = "ok"
    summary: str = ""

    def brief(self) -> str:
        args = ", ".join(f"{k}={v!r}" for k, v in self.arguments.items())
        return f"{self.tool}({args}) -> {self.status}: {self.summary}"


@dataclass
class NextBestAction:
    """A recommended policy action with its approval route and reason."""

    action: str
    route: str
    reason: str

    @property
    def rank(self) -> int:
        return _ROUTE_RANK.get(self.route, 0)

    def brief(self) -> str:
        return f"{self.action} ({self.route}) - {self.reason}"


@dataclass
class InvestigationReport:
    """The full structured output of one investigation."""

    transaction_id: str
    engine: str = "local"
    summary: str = ""
    verdict: str = "uncertain"  # fraud | legitimate | uncertain
    fraud_probability: float = 0.0
    evidence: List[EvidenceItem] = field(default_factory=list)
    risk_signals: List[RiskSignal] = field(default_factory=list)
    related_entities: List[str] = field(default_factory=list)
    historical_precedent: List[str] = field(default_factory=list)
    uncertainty: List[str] = field(default_factory=list)
    next_best_actions: List[NextBestAction] = field(default_factory=list)
    approval_route: str = "auto"
    reasoning: str = ""
    tool_calls: List[ToolCallRecord] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def top_severity(self) -> str:
        if not self.risk_signals:
            return "NONE"
        return max(self.risk_signals, key=lambda s: s.rank).severity

    @property
    def tools_called(self) -> List[str]:
        """Distinct MCP tool names invoked, in call order (deduplicated)."""
        seen: List[str] = []
        for call in self.tool_calls:
            if call.tool not in seen:
                seen.append(call.tool)
        return seen

    def error(self) -> Optional[Dict[str, Any]]:
        """Return the first tool error payload, if the investigation failed."""
        for call in self.tool_calls:
            if call.status != "ok" and call.summary.startswith("{"):
                try:
                    return {"tool": call.tool, "detail": json_loads(call.summary)}
                except Exception:  # pragma: no cover - defensive
                    return {"tool": call.tool, "detail": call.summary}
        return None

    def to_dict(self) -> Dict[str, Any]:
        """JSON-serializable view of the report (safe to log; no secrets)."""
        return asdict(self)


def json_loads(text: str) -> Any:
    import json

    return json.loads(text)
