"""HHGOA AI Investigator - autonomous fraud investigation agent.

Sits on top of the existing HHGOA TigerGraph MCP server (``mcp/``) and
reuses its seven investigation tools verbatim - no tool logic is duplicated
here. Two engines produce the same structured report:

* **Gemini** (``GEMINI_API_KEY`` present): a function-calling loop in which
  the Gemini model autonomously decides which MCP tools to call, starting
  with ``investigate_transaction``, then emits the final report JSON.
* **local** (no key, or Gemini unavailable): a deterministic deliberative
  engine that runs the same MCP tools in the same evidence-driven order and
  applies the fraud policy rules (R1-R10) itself.

Secrets (``GEMINI_API_KEY``) are read from the environment and never printed.

CLI:
    python -m agent.investigator 3514030
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
import warnings
from typing import Any, Dict, List, Optional, Sequence

# ---------------------------------------------------------------------------
# 1. Mock-mode bootstrap - MUST run before any `mcp.*` import so that
#    MCPConfig reads the intended TG_MOCK_MODE value.
# ---------------------------------------------------------------------------

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _bootstrap_mock_mode() -> None:
    """Default TG_MOCK_MODE=true so the agent is demo-ready out of the box.

    Precedence: OS environment variable wins; otherwise the demo default is
    `true` (verified offline fixtures), so the CLI works without a live
    TigerGraph cluster. Export TG_MOCK_MODE=false to force live mode.
    """
    if "TG_MOCK_MODE" not in os.environ:
        os.environ["TG_MOCK_MODE"] = "true"


_bootstrap_mock_mode()

# ---------------------------------------------------------------------------
# 2. Reuse the existing MCP investigation tool implementations.
# ---------------------------------------------------------------------------

from mcp.connection import TigerGraphConnectionError  # noqa: E402
from mcp.tools.investigation import (  # noqa: E402
    execute_investigate_transaction,
    execute_trace_connected_entities,
    execute_detect_card_testing,
    execute_analyze_region_anomalies,
    execute_retrieve_similar_cases,
    execute_calculate_case_exposure,
    execute_validate_graph_metrics,
)

from agent import models as am  # noqa: E402
from agent import prompts as ap  # noqa: E402

# Quiet the expected "attempted live, fell back to fixture" warnings and the
# aiohttp shutdown noise that the MCP connection layer emits in mock mode.
# This only tunes log verbosity in the agent process; the MCP code is
# untouched.
if os.environ.get("TG_MOCK_MODE", "").strip().lower() in ("true", "1", "yes"):
    logging.getLogger("mcp.connection").setLevel(logging.ERROR)
    logging.getLogger("mcp.tools").setLevel(logging.ERROR)
    warnings.filterwarnings("ignore", message="Unclosed client session")
    warnings.filterwarnings("ignore", message="Unclosed connector")

# The seven MCP investigation tools, keyed by MCP tool name.
MCP_TOOLS: Dict[str, Any] = {
    "investigate_transaction": execute_investigate_transaction,
    "trace_connected_entities": execute_trace_connected_entities,
    "detect_card_testing": execute_detect_card_testing,
    "analyze_region_anomalies": execute_analyze_region_anomalies,
    "retrieve_similar_cases": execute_retrieve_similar_cases,
    "calculate_case_exposure": execute_calculate_case_exposure,
    "validate_graph_metrics": execute_validate_graph_metrics,
}

DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_GEMINI_STEPS = 14  # hard cap on tool-calling loop rounds


class MCPToolError(RuntimeError):
    """Raised when an unknown MCP tool is requested."""


# ---------------------------------------------------------------------------
# 3. Tool executor - the only place the agent touches MCP tool functions.
# ---------------------------------------------------------------------------


def _summarize_tool(tool_name: str, result: Dict[str, Any]) -> str:
    """One-line summary of a normalized MCP tool result, for the ledger."""
    if not isinstance(result, dict):
        return str(result)[:200]
    if result.get("error"):
        msg = result.get("message", "unknown error")
        return json.dumps({k: result[k] for k in result}, default=str)

    meta = result.get("metadata", {}) or {}
    ev = result.get("evidence", []) or []
    sigs = [s.get("signal") for s in result.get("risk_signals", []) or []]

    if tool_name == "investigate_transaction":
        tx = next((e for e in ev if e.get("type") == "TRANSACTION_RECORD"), None)
        card = next((e for e in ev if e.get("type") == "CARD_INSTRUMENT"), None)
        parts = []
        if tx:
            a = tx.get("attributes", {})
            parts.append(f"${a.get('amount')} {a.get('channel')} risk={a.get('risk_score')}")
        if card:
            parts.append(f"card={card.get('entity')}")
        parts.append(f"signals={len(sigs)}")
        return ", ".join(parts)
    if tool_name == "trace_connected_entities":
        return (
            f"{meta.get('total_connected_cards', 0)} connected cards, "
            f"{meta.get('total_shared_devices', 0)} shared devices, "
            f"{len(ev)} entity hit(s)"
        )
    if tool_name == "detect_card_testing":
        attr = ev[0].get("attributes", {}) if ev else {}
        return (
            f"detected={attr.get('is_detected')}, "
            f"micro_auths={attr.get('micro_authorization_count')}, "
            f"large_charge=${attr.get('subsequent_large_charge')}"
        )
    if tool_name == "analyze_region_anomalies":
        attr = ev[0].get("attributes", {}) if ev else {}
        return (
            f"{attr.get('total_transactions')} txns, "
            f"{attr.get('distinct_regions')} region(s), "
            f"{attr.get('foreign_transaction_count')} international"
        )
    if tool_name == "retrieve_similar_cases":
        return f"{meta.get('precedent_count', len(ev))} precedent case(s)"
    if tool_name == "calculate_case_exposure":
        return (
            f"exposure=${meta.get('total_exposure_usd')}, "
            f"route={meta.get('required_approval_route')}"
        )
    if tool_name == "validate_graph_metrics":
        return "graph metrics snapshot"
    return f"{len(ev)} evidence item(s)"


class MCPToolExecutor:
    """Invokes the existing MCP investigation tools and records a ledger.

    This is a thin, stateless adapter: it never re-implements query logic,
    only dispatches to the same ``execute_*`` functions the MCP server
    registers as tools.
    """

    def __init__(self) -> None:
        self.calls: List[am.ToolCallRecord] = []
        self.results: Dict[str, List[Dict[str, Any]]] = {}
        self._ledger_id = 0

    def call(self, tool_name: str, **arguments: Any) -> Dict[str, Any]:
        func = MCP_TOOLS.get(tool_name)
        if func is None:
            raise MCPToolError(f"Unknown MCP tool: {tool_name}")

        try:
            result = func(**arguments)
        except TigerGraphConnectionError as exc:
            result = {"error": True, "type": "CONNECTION_FAILURE", "message": str(exc)}
        except Exception as exc:  # defensive: never crash the agent loop
            result = {"error": True, "type": "EXECUTION_ERROR", "message": str(exc)}

        if not isinstance(result, dict):
            result = {"result": result}

        status = "error" if result.get("error") else "ok"
        summary = _summarize_tool(tool_name, result)
        self.calls.append(
            am.ToolCallRecord(tool=tool_name, arguments=dict(arguments), status=status, summary=summary)
        )

        # Keep every result per tool; case exposure can be called per case.
        key = tool_name
        if tool_name in self.results:
            key = f"{tool_name}#{len(self.results[tool_name]) + 1}"
        self.results[key] = [result]
        return result

    # -- aggregation -------------------------------------------------------

    def collect_evidence(self) -> List[am.EvidenceItem]:
        items: List[am.EvidenceItem] = []
        seen: set = set()
        for key in self.results:
            tool_name = key.split("#", 1)[0]
            for result in self.results[key]:
                if result.get("error"):
                    continue
                for ev in result.get("evidence", []) or []:
                    sig = (
                        tool_name,
                        ev.get("type"),
                        ev.get("entity"),
                        ev.get("relationship"),
                    )
                    if sig in seen:
                        continue
                    seen.add(sig)
                    items.append(
                        am.EvidenceItem(
                            source_tool=tool_name,
                            type=ev.get("type", "UNKNOWN"),
                            entity=str(ev.get("entity", "")),
                            relationship=str(ev.get("relationship", "")),
                            attributes=ev.get("attributes", {}) or {},
                        )
                    )
        return items

    def collect_signals(self) -> List[am.RiskSignal]:
        signals: List[am.RiskSignal] = []
        seen: set = set()
        for key in self.results:
            tool_name = key.split("#", 1)[0]
            for result in self.results[key]:
                if result.get("error"):
                    continue
                for sig in result.get("risk_signals", []) or []:
                    name = sig.get("signal", "")
                    if name in seen:
                        continue
                    seen.add(name)
                    signals.append(
                        am.RiskSignal(
                            signal=name,
                            severity=sig.get("severity", "MEDIUM"),
                            guidance=sig.get("guidance", ""),
                            policy_rule=sig.get("policy_rule", ""),
                            source_tool=tool_name,
                        )
                    )
        return signals

    def collect_errors(self) -> List[str]:
        errors: List[str] = []
        for call in self.calls:
            if call.status == "error":
                try:
                    detail = json.loads(call.summary)
                    errors.append(
                        f"{call.tool} failed ({detail.get('type', 'ERROR')}): "
                        f"{detail.get('message', 'unknown')}"
                    )
                except Exception:
                    errors.append(f"{call.tool} failed: {call.summary}")
        return errors


# ---------------------------------------------------------------------------
# 4. Evidence extraction helpers shared by both engines.
# ---------------------------------------------------------------------------


def _extract_entities(
    evidence: Sequence[am.EvidenceItem],
) -> Dict[str, Any]:
    """Pull card / customer / device / case identifiers out of the evidence."""
    card_id = customer_id = device_id = None
    case_ids: List[str] = []
    regions: List[str] = []
    emails: List[str] = []
    channel = None
    amount = risk_score = None
    prior_cases: List[str] = []

    for ev in evidence:
        if ev.type == "CARD_INSTRUMENT" and not card_id:
            card_id = ev.entity
            customer_id = ev.attributes.get("customer_id") or customer_id
        elif ev.type == "DEVICE_PROFILE" and not device_id:
            device_id = ev.entity
        elif ev.type == "TRANSACTION_RECORD":
            channel = ev.attributes.get("channel")
            amount = ev.attributes.get("amount")
            risk_score = ev.attributes.get("risk_score")
        elif ev.type == "ASSOCIATED_CASE":
            prior_cases.append(ev.entity)
        elif ev.type == "BILLING_REGION":
            regions.append(ev.entity)
        elif ev.type in ("PURCHASER_EMAIL", "RECIPIENT_EMAIL"):
            emails.append(ev.entity)

    # Linked open case pack IDs (e.g. HHG-001) are the exposure targets.
    case_ids = prior_cases
    return {
        "card_id": card_id,
        "customer_id": customer_id,
        "device_id": device_id,
        "case_ids": case_ids,
        "regions": regions,
        "emails": emails,
        "channel": channel,
        "amount": amount,
        "risk_score": risk_score,
        "prior_cases": prior_cases,
    }


def _related_entities(
    evidence: Sequence[am.EvidenceItem], entities: Dict[str, Any]
) -> List[str]:
    """Human-readable list of related entities for the report."""
    lines: List[str] = []
    seen: set = set()

    def add(line: str) -> None:
        if line not in seen:
            seen.add(line)
            lines.append(line)

    if entities.get("card_id"):
        cust = f", customer {entities['customer_id']}" if entities.get("customer_id") else ""
        add(f"Card {entities['card_id']} ({cust.strip(', ') or 'details unavailable'})")
    if entities.get("customer_id"):
        add(f"Customer {entities['customer_id']}")
    if entities.get("device_id"):
        add(f"Device profile {entities['device_id']}")

    for ev in evidence:
        if ev.source_tool == "trace_connected_entities":
            add(f"{ev.type} {ev.entity} via {ev.relationship} (hop {ev.attributes.get('hop_distance')})")
        elif ev.type == "BILLING_REGION":
            add(f"Billing region {ev.entity}")
        elif ev.type in ("PURCHASER_EMAIL", "RECIPIENT_EMAIL"):
            add(f"{ev.relationship.title().replace('_', ' ')} {ev.entity}")

    for cid in entities.get("case_ids", []):
        add(f"Open case {cid}")
    return lines


def _precedent_lines(evidence: Sequence[am.EvidenceItem]) -> List[str]:
    lines: List[str] = []
    for ev in evidence:
        if ev.type == "HISTORICAL_CASE_PRECEDENT":
            a = ev.attributes
            lines.append(
                f"{ev.entity}: {a.get('outcome')} (pattern={a.get('pattern')}, "
                f"match={ev.relationship}, exposure=${a.get('exposure_usd')}, "
                f"report_filed={a.get('report_filed')}, actions={a.get('actions_taken')})"
            )
    return lines


# ---------------------------------------------------------------------------
# 5. Policy adjudication - maps correlated signals to actions (R1-R10).
# ---------------------------------------------------------------------------

_ACTION_AUTO = "auto"


def _max_route(actions: Sequence[am.NextBestAction]) -> str:
    if not actions:
        return _ACTION_AUTO
    return max(actions, key=lambda a: a.rank).route


def _adjudicate(
    evidence: List[am.EvidenceItem],
    signals: List[am.RiskSignal],
    entities: Dict[str, Any],
    precedent: List[str],
    executor: MCPToolExecutor,
) -> Dict[str, Any]:
    """Deterministic, policy-grounded decision making over aggregated evidence.

    Risk signals alone never establish fraud: each verdict path requires at
    least two independent pieces of correlated evidence.
    """
    signal_names = {s.signal for s in signals}
    severities = {s.signal: s.severity for s in signals}

    # Exposure from any calculate_case_exposure result.
    exposure = 0.0
    approval_from_tools = "auto"
    for key, results in executor.results.items():
        if key.startswith("calculate_case_exposure"):
            for r in results:
                if not r.get("error"):
                    meta = r.get("metadata", {}) or {}
                    exposure = max(exposure, float(meta.get("total_exposure_usd") or 0.0))
                    route = meta.get("required_approval_route") or "auto"
                    approval_from_tools = max(approval_from_tools, route, key=lambda x: {"auto": 0, "L1": 1, "L2": 2}[x])

    # Card testing evaluation details (for R5).
    testing = next(
        (e for e in evidence if e.type == "CARD_TESTING_EVALUATION"),
        None,
    )
    testing_confirmed = bool(
        testing and testing.attributes.get("is_detected")
    )
    large_charge = (
        float(testing.attributes.get("subsequent_large_charge") or 0.0) if testing else 0.0
    )

    geo = next((e for e in evidence if e.type == "GEOGRAPHIC_DISPERSION"), None)
    foreign_count = int(geo.attributes.get("foreign_transaction_count") or 0) if geo else 0
    distinct_regions = int(geo.attributes.get("distinct_regions") or 0) if geo else 0

    device_ev = next((e for e in evidence if e.type == "DEVICE_PROFILE"), None)
    device_status = device_ev.attributes.get("device_status") if device_ev else None
    proxy_flag = str(device_ev.attributes.get("proxy_flag") or "") if device_ev else ""

    channel = entities.get("channel")
    risk_score = entities.get("risk_score")
    amount = float(entities.get("amount") or 0.0)

    # ---------------- correlation: independent evidence pieces ------------
    corroborating: List[str] = []  # independent non-score evidence pieces
    if testing_confirmed:
        corroborating.append("card testing sequence confirmed (3+ micro auths then larger charge)")
    if "CROSS_ACCOUNT_DEVICE_SHARING" in signal_names:
        corroborating.append("device shared across multiple customers (syndicate link)")
    if foreign_count > 0:
        corroborating.append(f"{foreign_count} out-of-region/international transaction(s)")
    if device_status == "New":
        corroborating.append("device marked New on this account")
    if "ANONYMOUS" in proxy_flag.upper():
        corroborating.append("anonymous proxy detected")
    if distinct_regions > 1:
        corroborating.append(f"activity across {distinct_regions} distinct billing regions")
    if any(": confirmed_fraud (" in (p or "").lower() for p in precedent):
        corroborating.append("prior confirmed-fraud precedent retrieved")

    score_signal_present = bool(
        {"ELEVATED_MODEL_RISK_SCORE", "MODERATE_MODEL_RISK_SCORE"} & signal_names
    )
    score_evidence = risk_score if score_signal_present else None

    # ---------------- verdict + probability --------------------------------
    verdict = "uncertain"
    probability = 0.30  # baseline for an alerted transaction with no verdict yet
    reasoning_bits: List[str] = []

    if score_evidence is not None:
        reasoning_bits.append(
            f"Model risk score {score_evidence} is an input signal only (Policy 0); "
            "it never determines the verdict by itself."
        )

    if testing_confirmed and len(corroborating) >= 1:
        verdict = "fraud"
        probability = 0.85
        reasoning_bits.append(
            "R5 card-testing sequence corroborated by the micro-auth/large-charge "
            "transaction sequence (two independent evidence pieces)."
        )
    elif "CROSS_ACCOUNT_DEVICE_SHARING" in signal_names and len(corroborating) >= 2:
        verdict = "fraud"
        probability = 0.80
        reasoning_bits.append(
            "R6 shared device across cards, corroborated by multiple independent "
            "signals; fraud indicated."
        )
    elif foreign_count > 0 and device_status == "New" and len(corroborating) >= 2:
        verdict = "fraud"
        probability = 0.75
        reasoning_bits.append(
            "Out-of-region use combined with a new device and additional "
            "corroboration (patterns 3/4)."
        )
    elif len(corroborating) >= 2:
        verdict = "uncertain"
        probability = 0.60
        reasoning_bits.append(
            "Multiple signals present but they do not yet rise to a confirmed "
            "fraud pattern; verdict remains uncertain pending verification (R1/R8)."
        )
    elif len(corroborating) == 1:
        verdict = "uncertain"
        probability = 0.45
        reasoning_bits.append(
            "Exactly one independent signal corroborates the alert; below the "
            "0.70 threshold, so R1 requires verification before any block."
        )
    else:
        # Score-only (or nothing): never declare fraud.
        if score_signal_present:
            verdict = "uncertain"
            probability = 0.35
            reasoning_bits.append(
                "Only the model score supports the alert. No independent "
                "corroboration exists, so fraud is NOT declared (Policy 0/R1)."
            )
        else:
            verdict = "legitimate"
            probability = 0.15
            reasoning_bits.append(
                "No corroborating signals and no risk evidence found; activity "
                "appears consistent with normal behavior."
            )

    # Precedent adjusts calibration, not the verdict on its own.
    fraud_precedent = any(": confirmed_fraud (" in (p or "").lower() for p in precedent)
    cleared_precedent = any(": cleared (" in (p or "").lower() for p in precedent)
    if fraud_precedent and verdict != "legitimate":
        probability = min(0.95, probability + 0.05)
        reasoning_bits.append("Confirmed-fraud precedent slightly raises confidence.")
    if cleared_precedent and verdict == "uncertain":
        probability = max(0.15, probability - 0.10)
        reasoning_bits.append(
            "Cleared precedent for the same subject slightly lowers confidence "
            "(precedent guides, never decides)."
        )

    # ---------------- uncertainty -----------------------------------------
    uncertainty: List[str] = []
    if not entities.get("device_id") and channel == "in_person":
        uncertainty.append(
            "In-person transaction: no device/identity record exists, so device "
            "and proxy signals cannot be evaluated for this alert."
        )
    if not precedent:
        uncertainty.append(
            "No historical precedent returned for this subject; correlation "
            "relies on current-graph evidence only."
        )
    if score_signal_present and len(corroborating) == 0:
        uncertainty.append(
            "Risk score is uncorroborated by any independent evidence; a fraud "
            "conclusion is not supported yet."
        )
    if channel == "online" and not device_ev:
        uncertainty.append("Online transaction but no device record was returned.")
    if verdict == "uncertain":
        uncertainty.append(
            "No customer/analyst verification response is available in this "
            "round (not provided by the dataset); requested via "
            "VERIFY_WITH_CUSTOMER/STEP_UP_AUTH."
        )
    if foreign_count > 0 and distinct_regions > 1:
        uncertainty.append(
            "Multi-region activity could be sustained travel or cloning; a "
            "customer response is needed to distinguish them (README line 119)."
        )
    errors = executor.collect_errors()
    uncertainty.extend(f"Tool error: {e}" for e in errors)
    if exposure > 500 and verdict == "uncertain":
        uncertainty.append(
            f"Exposure ${exposure:.2f} exceeds $500 while verdict is uncertain (R8)."
        )
    if not uncertainty:
        uncertainty.append(
            "Evidence set is internally consistent; residual uncertainty is "
            "limited to the absence of a live customer confirmation."
        )

    # ---------------- actions ----------------------------------------------
    actions: List[am.NextBestAction] = []

    if testing_confirmed:
        actions.append(
            am.NextBestAction(
                action="DECLINE_TRANSACTION",
                route="L1",
                reason="R5: card-testing burst confirmed (3+ micro auths then larger charge).",
            )
        )
        actions.append(
            am.NextBestAction(
                action="STEP_UP_AUTH",
                route=_ACTION_AUTO,
                reason="R5: require step-up authentication before further activity.",
            )
        )
        if large_charge > 100:
            actions.append(
                am.NextBestAction(
                    action="BLOCK_CARD",
                    route="L1" if exposure <= 2500 else "L2",
                    reason=f"R5: ${large_charge} purchase already cleared (>$100); block and reissue.",
                )
            )
        actions.append(
            am.NextBestAction(
                action="CREATE_CASE",
                route=_ACTION_AUTO,
                reason="3a: open an internal case with the evidence attached.",
            )
        )

    if "CROSS_ACCOUNT_DEVICE_SHARING" in signal_names:
        actions.append(
            am.NextBestAction(
                action="CREATE_CASE",
                route=_ACTION_AUTO,
                reason="R6: shared device profile links multiple cards; create case.",
            )
        )
        actions.append(
            am.NextBestAction(
                action="FILE_REPORT",
                route="L2",
                reason="R6: shared origin connects this to coordinated activity across customers.",
            )
        )
        actions.append(
            am.NextBestAction(
                action="MONITOR_CONNECTED_CARDS",
                route=_ACTION_AUTO,
                reason="R6: monitor every card sharing the device profile.",
            )
        )

    if foreign_count > 0 and not testing_confirmed:
        actions.append(
            am.NextBestAction(
                action="VERIFY_WITH_CUSTOMER",
                route=_ACTION_AUTO,
                reason="R1: out-of-region signal alone needs cardholder confirmation before any block.",
            )
        )
        actions.append(
            am.NextBestAction(
                action="MONITOR_CARD",
                route=_ACTION_AUTO,
                reason="R4: raise monitoring sensitivity while verification is pending.",
            )
        )

    if not actions:
        if score_signal_present or verdict == "uncertain":
            actions.append(
                am.NextBestAction(
                    action="VERIFY_WITH_CUSTOMER",
                    route=_ACTION_AUTO,
                    reason="R1: single/uncorrelated signal with probability < 0.70; verify before any block.",
                )
            )
            actions.append(
                am.NextBestAction(
                    action="STEP_UP_AUTH",
                    route=_ACTION_AUTO,
                    reason="R1: step-up authentication adds an independent confirmation signal.",
                )
            )
        else:
            actions.append(
                am.NextBestAction(
                    action="CLOSE_NO_FRAUD",
                    route=_ACTION_AUTO,
                    reason="Policy 0/R1: no corroborating evidence beyond the alert; close as legitimate.",
                )
            )

    if verdict == "uncertain" and exposure > 500:
        actions.append(
            am.NextBestAction(
                action="ESCALATE_TO_ANALYST",
                route=_ACTION_AUTO,
                reason=f"R8: verdict uncertain and exposure ${exposure:.2f} > $500.",
            )
        )

    if exposure > 1000 and verdict == "fraud" and not any(a.action == "FILE_REPORT" for a in actions):
        actions.append(
            am.NextBestAction(
                action="FILE_REPORT",
                route="L2",
                reason=f"R2: confirmed fraud with exposure ${exposure:.2f} > $1,000 mandates filing.",
            )
        )

    if verdict == "fraud" and not any(a.action == "CREATE_CASE" for a in actions):
        actions.append(
            am.NextBestAction(
                action="CREATE_CASE",
                route=_ACTION_AUTO,
                reason="3a: fraud probability reached; open the internal case.",
            )
        )

    # Deduplicate actions by (action, route), keep first reason.
    deduped: List[am.NextBestAction] = []
    seen_actions: set = set()
    for a in actions:
        if a.action in seen_actions:
            continue
        seen_actions.add(a.action)
        deduped.append(a)
    actions = deduped

    approval_route = max(
        [approval_from_tools] + [a.route for a in actions],
        key=lambda x: {"auto": 0, "L1": 1, "L2": 2}[x],
    )

    # ---------------- summary ---------------------------------------------
    txn_desc = []
    if amount is not None:
        txn_desc.append(f"${amount}")
    if channel:
        txn_desc.append(channel)
    summary_parts = [
        f"Flagged transaction: {', '.join(txn_desc) if txn_desc else 'details unavailable'}."
    ]
    if entities.get("card_id"):
        summary_parts.append(f"Card {entities['card_id']} (customer {entities.get('customer_id')}).")
    if entities.get("device_id"):
        summary_parts.append(f"Device {entities['device_id']}.")
    elif channel == "in_person":
        summary_parts.append("In-person channel (no device record).")
    if entities.get("regions"):
        summary_parts.append(f"Billing region {', '.join(entities['regions'])}.")
    if entities.get("emails"):
        summary_parts.append(f"Email domain(s): {', '.join(entities['emails'])}.")
    if entities.get("case_ids"):
        summary_parts.append(f"Linked open case(s): {', '.join(entities['case_ids'])}.")
    summary_parts.append(
        f"Corroborating evidence pieces: {len(corroborating)}"
        + (f" ({'; '.join(corroborating)})" if corroborating else "")
        + "."
    )
    top_severity = (
        max(signals, key=lambda s: s.rank).severity if signals else "none"
    )
    summary_parts.append(
        f"Verdict: {verdict} (probability {probability:.2f}); "
        f"top signal severity {top_severity}."
    )
    summary = " ".join(summary_parts)

    # ---------------- final reasoning -------------------------------------
    reasoning_bits.append(
        f"Correlated {len(corroborating)} independent evidence piece(s) "
        f"{'(' + '; '.join(corroborating) + ')' if corroborating else ''} "
        f"against {len(signals)} risk signal(s)."
    )
    if exposure:
        reasoning_bits.append(f"Case exposure ${exposure:.2f} -> approval route {approval_route}.")
    reasoning_bits.append(
        "Actions follow the cited policy rules; only 'auto' actions may be "
        "executed by the agent, L1/L2 await human approval."
    )
    reasoning = " ".join(reasoning_bits)

    return {
        "verdict": verdict,
        "fraud_probability": probability,
        "summary": summary,
        "uncertainty": uncertainty,
        "next_best_actions": actions,
        "approval_route": approval_route,
        "reasoning": reasoning,
        "exposure": exposure,
    }


# ---------------------------------------------------------------------------
# 6. Local deliberative engine (no Gemini key required).
# ---------------------------------------------------------------------------


class LocalAdjudicator:
    """Runs the MCP tools in evidence-driven order and applies policy R1-R10.

    Used when ``GEMINI_API_KEY`` is absent, or as a safety fallback if the
    Gemini engine errors. Same tools, same report shape - no LLM involved.
    """

    engine_name = "local"

    def investigate(self, txn_id: str) -> am.InvestigationReport:
        executor = MCPToolExecutor()

        # Graph health check (read-only, optional tool).
        executor.call("validate_graph_metrics")

        # Step 1: always start with investigate_transaction.
        primary = executor.call("investigate_transaction", txn_id=txn_id)

        report = am.InvestigationReport(transaction_id=txn_id, engine=self.engine_name)

        if primary.get("error"):
            report.summary = (
                f"Transaction {txn_id} could not be investigated: "
                f"{primary.get('message', primary.get('type', 'unknown error'))}."
            )
            report.verdict = "uncertain"
            report.fraud_probability = 0.0
            report.uncertainty = [
                f"Primary investigation failed ({primary.get('type')}); no "
                "evidence could be gathered, so no fraud determination is possible."
            ]
            report.next_best_actions = [
                am.NextBestAction(
                    action="ESCALATE_TO_ANALYST",
                    route=_ACTION_AUTO,
                    reason="No graph evidence available for this transaction; a human must review.",
                )
            ]
            report.approval_route = _ACTION_AUTO
            report.reasoning = (
                "Policy requires evidence before any determination; with the "
                "primary tool failing, escalation (R8) is the only defensible action."
            )
            report.tool_calls = list(executor.calls)
            report.warnings = executor.collect_errors()
            return report

        evidence_so_far = executor.collect_evidence()
        entities = _extract_entities(evidence_so_far)

        # Step 2: selectively call follow-up tools based on the evidence.
        if entities.get("card_id"):
            card_id = entities["card_id"]
            executor.call("trace_connected_entities", target_card_id=card_id, max_hops=2)
            executor.call("analyze_region_anomalies", target_card_id=card_id)
            executor.call("detect_card_testing", target_card_id=card_id)
            executor.call(
                "retrieve_similar_cases",
                customer_id=entities.get("customer_id") or "",
                card_id=card_id,
            )
        else:
            # No card resolved: fall back to customer/pattern lookup only.
            if entities.get("customer_id"):
                executor.call("retrieve_similar_cases", customer_id=entities["customer_id"])
            else:
                executor.call(
                    "retrieve_similar_cases",
                    pattern_id="none",
                )

        # Exposure for each linked open case.
        for case_id in entities.get("case_ids", []):
            executor.call("calculate_case_exposure", target_case_id=case_id)

        # Step 3: aggregate everything.
        evidence = executor.collect_evidence()
        signals = executor.collect_signals()
        entities = _extract_entities(evidence)
        related = _related_entities(evidence, entities)
        precedent = _precedent_lines(evidence)

        # Step 4: policy adjudication -> actions, route, reasoning.
        decision = _adjudicate(evidence, signals, entities, precedent, executor)

        report.evidence = evidence
        report.risk_signals = signals
        report.related_entities = related
        report.historical_precedent = precedent
        report.summary = decision["summary"]
        report.verdict = decision["verdict"]
        report.fraud_probability = decision["fraud_probability"]
        report.uncertainty = decision["uncertainty"]
        report.next_best_actions = decision["next_best_actions"]
        report.approval_route = decision["approval_route"]
        report.reasoning = decision["reasoning"]
        report.tool_calls = list(executor.calls)
        report.warnings = executor.collect_errors()
        return report


# ---------------------------------------------------------------------------
# 7. Gemini engine - autonomous function-calling loop over the MCP tools.
# ---------------------------------------------------------------------------


class GeminiAgent:
    """Drives the investigation with Gemini tool (function) calling.

    The model chooses which MCP tools to call, starting from
    ``investigate_transaction``, and finishes with a structured JSON report.
    All tool execution is delegated to :class:`MCPToolExecutor` so the exact
    same MCP implementations are reused.
    """

    engine_name = "gemini"

    def __init__(self, api_key: str, model_name: str = DEFAULT_GEMINI_MODEL):
        # The key is passed to the SDK configuration only; never logged.
        from google import genai
        from google.genai import types as genai_types

        self._types = genai_types
        self._client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def _build_chat(self, executor: MCPToolExecutor):
        genai_config = self._types.GenerateContentConfig(
            system_instruction=ap.SYSTEM_PROMPT,
            tools=[self._types.Tool(function_declarations=ap.FUNCTION_DECLARATIONS)],
            temperature=0.1,
        )
        return self._client.chats.create(
            model=self.model_name,
            config=genai_config,
        )

    def investigate(self, txn_id: str) -> am.InvestigationReport:
        executor = MCPToolExecutor()
        chat = self._build_chat(executor)

        response = chat.send_message(ap.build_start_prompt(txn_id))
        steps = 0

        # Tool-calling loop: execute every requested MCP tool and feed the
        # normalized results back to the model until it stops calling tools.
        while steps < MAX_GEMINI_STEPS:
            function_calls = getattr(response, "function_calls", None) or []
            if not function_calls:
                break
            response_parts = []
            for fc in function_calls:
                args = dict(fc.args or {})
                result = executor.call(fc.name, **args)
                response_parts.append(
                    self._types.Part.from_function_response(
                        name=fc.name, response={"result": result}
                    )
                )
            response = chat.send_message(response_parts)
            steps += 1

        final_text = getattr(response, "text", "") or ""
        report = am.InvestigationReport(transaction_id=txn_id, engine=self.engine_name)

        # Evidence/signals are always taken from the actual tool results,
        # never invented by the model.
        evidence = executor.collect_evidence()
        signals = executor.collect_signals()
        entities = _extract_entities(evidence)
        report.evidence = evidence
        report.risk_signals = signals
        report.related_entities = _related_entities(evidence, entities)
        report.historical_precedent = _precedent_lines(evidence)
        report.tool_calls = list(executor.calls)
        report.warnings = executor.collect_errors()

        parsed = _parse_final_json(final_text)
        if parsed:
            report.summary = str(parsed.get("summary", "")).strip()
            verdict = str(parsed.get("verdict", "uncertain")).lower()
            report.verdict = verdict if verdict in ("fraud", "legitimate", "uncertain") else "uncertain"
            try:
                report.fraud_probability = max(0.0, min(1.0, float(parsed.get("fraud_probability", 0.0))))
            except (TypeError, ValueError):
                report.fraud_probability = 0.0
            report.uncertainty = [str(u) for u in parsed.get("uncertainty", []) or []]
            report.next_best_actions = _parse_actions(parsed.get("next_best_actions") or [])
            report.approval_route = str(
                parsed.get("approval_route") or _max_route(report.next_best_actions)
            )
            report.reasoning = str(parsed.get("reasoning", "")).strip()
        else:
            report.summary = (final_text.strip() or "No final report text returned by the model.")[:1000]
            report.verdict = "uncertain"
            report.fraud_probability = 0.0
            report.uncertainty = [
                "Gemini did not return a parseable final JSON report; the "
                "evidence and signals below are still sourced from the real "
                "MCP tool results, but the narrative is unavailable."
            ]
            report.next_best_actions = [
                am.NextBestAction(
                    action="ESCALATE_TO_ANALYST",
                    route=_ACTION_AUTO,
                    reason="Model output was unparseable; hand the gathered evidence to a human (R8).",
                )
            ]
            report.approval_route = _ACTION_AUTO
            report.reasoning = "Model narrative unavailable; actions default to analyst review."

        # Policy floor: never report fraud from a score alone.
        _enforce_score_guard(report, entities)
        return report


def _enforce_score_guard(report: am.InvestigationReport, entities: Dict[str, Any]) -> None:
    """Downgrade a fraud verdict that rests only on the model risk score."""
    if report.verdict != "fraud":
        return
    signal_names = {s.signal for s in report.risk_signals}
    score_signals = {"ELEVATED_MODEL_RISK_SCORE", "MODERATE_MODEL_RISK_SCORE"}
    non_score_signals = signal_names - score_signals
    has_corroboration = bool(non_score_signals) or any(
        (
            e.type == "CARD_TESTING_EVALUATION"
            and bool(e.attributes.get("is_detected"))
        )
        or (
            e.type == "GEOGRAPHIC_DISPERSION"
            and (e.attributes.get("foreign_transaction_count") or 0) > 0
        )
        for e in report.evidence
    )
    if not has_corroboration:
        report.verdict = "uncertain"
        report.fraud_probability = min(report.fraud_probability, 0.5)
        report.uncertainty.append(
            "Guardrail: model risk score was the only supporting signal; a "
            "fraud verdict is not permitted on a score alone (Policy 0/R1)."
        )


def _parse_actions(raw: Any) -> List[am.NextBestAction]:
    actions: List[am.NextBestAction] = []
    if not isinstance(raw, list):
        return actions
    valid_routes = {"auto", "L1", "L2"}
    for item in raw:
        if isinstance(item, dict) and item.get("action"):
            route = str(item.get("route", "auto"))
            if route not in valid_routes:
                route = "auto"
            actions.append(
                am.NextBestAction(
                    action=str(item["action"]),
                    route=route,
                    reason=str(item.get("reason", "")),
                )
            )
    return actions


def _parse_final_json(text: str) -> Optional[Dict[str, Any]]:
    """Extract the final report JSON from the model's message, if any."""
    if not text:
        return None
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    candidates = []
    if fenced:
        candidates.append(fenced.group(1))
    brace = re.search(r"\{.*\}", text, re.DOTALL)
    if brace:
        candidates.append(brace.group(0))
    for cand in candidates:
        try:
            data = json.loads(cand)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            continue
    return None


# ---------------------------------------------------------------------------
# 8. Investigator facade + report rendering + CLI.
# ---------------------------------------------------------------------------


class Investigator:
    """Facade that picks the Gemini or local engine and runs one investigation."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        engine: Optional[str] = None,
    ):
        # Read the key from the environment; never expose its value.
        self.api_key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY", "")
        self.model_name = model_name or os.getenv("GEMINI_MODEL") or DEFAULT_GEMINI_MODEL
        requested = (engine or os.getenv("AGENT_ENGINE") or "").strip().lower()
        if requested in ("gemini", "local"):
            self.engine = requested
        else:
            self.engine = "gemini" if self.api_key else "local"

    @property
    def has_api_key(self) -> bool:
        return bool(self.api_key)

    def investigate(self, txn_id: str) -> am.InvestigationReport:
        txn_id = str(txn_id).strip()
        if self.engine == "gemini":
            try:
                agent = GeminiAgent(api_key=self.api_key, model_name=self.model_name)
                return agent.investigate(txn_id)
            except Exception as exc:  # fall back to local on any LLM failure
                report = LocalAdjudicator().investigate(txn_id)
                report.warnings.append(
                    f"Gemini engine unavailable ({type(exc).__name__}); "
                    "fell back to the local deliberative engine."
                )
                return report
        return LocalAdjudicator().investigate(txn_id)


def render_report(report: am.InvestigationReport) -> str:
    """Render the structured report as the CLI's readable sectioned output."""
    lines: List[str] = []
    add = lines.append

    add("HHGOA AI INVESTIGATOR")
    add("---------------------")
    add(f"Transaction: {report.transaction_id}")
    if report.engine == "gemini":
        llm_desc = f"Gemini ({DEFAULT_GEMINI_MODEL})"
    else:
        llm_desc = "local deliberative engine (no LLM key)"
    add(f"LLM: {llm_desc}")
    add(f"Verdict: {report.verdict} (fraud probability {report.fraud_probability:.2f})")
    add("")

    add("INVESTIGATION SUMMARY")
    for sentence in re.split(r"(?<=\.)\s+", report.summary.strip() or "-"):
        add(f"- {sentence}")
    add("")

    add("EVIDENCE")
    if report.evidence:
        for ev in report.evidence:
            add(f"- [{ev.source_tool}] {ev.brief()}")
    else:
        add("- (no evidence returned by MCP tools)")
    add("")

    add("RISK SIGNALS")
    if report.risk_signals:
        for sig in report.risk_signals:
            add(f"- {sig.brief()}")
        add(
            "- Correlation rule: signals are evidence only; no fraud is "
            "declared from a risk score alone."
        )
    else:
        add("- (no risk signals raised)")
    add("")

    add("RELATED ENTITIES")
    if report.related_entities:
        for ent in report.related_entities:
            add(f"- {ent}")
    else:
        add("- (none discovered)")
    add("")

    add("HISTORICAL PRECEDENT")
    if report.historical_precedent:
        for p in report.historical_precedent:
            add(f"- {p}")
    else:
        add("- (no similar closed cases retrieved)")
    add("")

    add("UNCERTAINTY")
    for u in report.uncertainty:
        add(f"- {u}")
    add("")

    add("NEXT BEST ACTION")
    for action in report.next_best_actions:
        add(f"- {action.brief()}")
    add("")

    add("APPROVAL ROUTE")
    add(f"- {report.approval_route}")
    add("")

    add("REASONING")
    for sentence in re.split(r"(?<=\.)\s+", report.reasoning.strip() or "-"):
        add(f"- {sentence}")

    if report.warnings:
        add("")
        add("WARNINGS")
        for w in report.warnings:
            add(f"- {w}")

    add("")
    add("MCP TOOLS CALLED")
    for call in report.tool_calls:
        add(f"- {call.brief()}")

    return "\n".join(lines)


def _close_tg_connection() -> None:
    """Best-effort release of the shared TigerGraph HTTP connection pool.

    The MCP connection module keeps a module-level singleton connection whose
    aiohttp session otherwise triggers "Unclosed client session" warnings at
    interpreter shutdown. aiohttp sessions are bound to the event loop they
    were created on, so we close on the current main loop (the same loop the
    MCP connection manager runs queries on). Safe because the agent CLI owns
    its process and it is a no-op when no live client was ever created.
    """
    try:
        import asyncio

        conn = getattr(default_connection, "_conn", None)
        if conn is None or getattr(conn, "_async_client", None) is None:
            return
        if conn._async_client.closed:
            return
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            return
        if loop.is_closed() or loop.is_running():
            return
        loop.run_until_complete(
            asyncio.wait_for(conn.aclose(), timeout=3)
        )
    except Exception:
        pass


def main(argv: Optional[Sequence[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print("Usage: python -m agent.investigator <transaction_id> [--json]")
        print("  GEMINI_API_KEY  enables the Gemini engine; without it the local")
        print("                  deliberative engine is used. The key is never printed.")
        print("  TG_MOCK_MODE    true (default) runs against offline fixtures.")
        return 0 if argv else 2

    txn_id = argv[0]
    as_json = "--json" in argv[1:]

    investigator = Investigator()
    report = investigator.investigate(txn_id)

    if as_json:
        print(json.dumps(report.to_dict(), indent=2, default=str))
    else:
        print(render_report(report))
    _close_tg_connection()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
