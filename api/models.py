"""
HHGOA API response models.

Pydantic models define the /investigate response contract exactly once.
The API layer serialises the InvestigationReport into these models;
nothing downstream needs to know about dataclasses or asdict().
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------

class InvestigationSummary(BaseModel):
    verdict: str = Field(description="fraud | legitimate | uncertain")
    fraud_probability: float = Field(ge=0.0, le=1.0)
    summary: str


class EvidenceItem(BaseModel):
    source_tool: str
    type: str
    entity: str
    relationship: str
    attributes: Dict[str, Any] = Field(default_factory=dict)


class RiskSignal(BaseModel):
    signal: str
    severity: str
    guidance: str
    policy_rule: str = ""
    source_tool: str = ""


class NextBestAction(BaseModel):
    action: str
    route: str = Field(description="auto | L1 | L2")
    reason: str


class ToolCallRecord(BaseModel):
    tool: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    status: str
    summary: str


class ExposureSummary(BaseModel):
    total_exposure_usd: float = 0.0
    fraud_transaction_count: int = 0
    required_approval_route: str = "auto"


# ---------------------------------------------------------------------------
# Top-level response
# ---------------------------------------------------------------------------

class InvestigationResponse(BaseModel):
    """
    Stable /investigate response contract.

    Fields are grouped by concern so consumers can parse only what they need:
      - status / transaction_id / engine  — envelope
      - investigation                     — verdict + probability + summary
      - evidence                          — every evidence item from MCP tools
      - risk_signals                      — signals raised across all tools
      - connected_entities                — related entity strings
      - historical_context                — closed-case precedents
      - exposure                          — financial impact summary
      - uncertainty                       — open questions / missing evidence
      - next_best_actions                 — full ordered action list
      - next_best_action                  — top action name (convenience)
      - approval_route                    — highest route across all actions
      - explanation                       — policy-grounded reasoning
      - tools_called                      — ordered list of MCP tool names
      - tool_audit                        — full per-call ledger
      - warnings                          — non-fatal issues
    """
    status: str = Field(default="ok", description="ok | error")
    transaction_id: str
    engine: str = Field(description="gemini | local")

    investigation: InvestigationSummary
    evidence: List[EvidenceItem]
    risk_signals: List[RiskSignal]

    connected_entities: List[str] = Field(default_factory=list)
    historical_context: List[str] = Field(default_factory=list)
    exposure: ExposureSummary = Field(default_factory=ExposureSummary)
    uncertainty: List[str] = Field(default_factory=list)

    next_best_actions: List[NextBestAction] = Field(default_factory=list)
    next_best_action: str = ""
    approval_route: str = "auto"

    explanation: str = Field(default="", description="Policy-grounded reasoning (no hidden chain-of-thought)")

    tools_called: List[str] = Field(default_factory=list, description="Ordered distinct MCP tool names")
    tool_audit: List[ToolCallRecord] = Field(default_factory=list, description="Full per-call ledger")
    warnings: List[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    status: str = "error"
    error_code: str
    message: str
    transaction_id: Optional[str] = None
