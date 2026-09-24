"""Tests for the HHGOA AI Investigator Agent.

Run with:
    python -m pytest tests/test_agent_investigator.py -v
or directly:
    python tests/test_agent_investigator.py

Covered:
1. Syntax/import smoke tests for all agent modules.
2. Mock end-to-end investigation (local deliberative engine) on txn 3514030.
3. The no-fraud-from-score-alone guardrail.
4. Graceful handling of a missing transaction.
5. The Gemini function-calling loop (stubbed model, real MCP tool execution).
6. CLI entry points (render + --json).
"""

import importlib
import json
import os
import sys

# Simulated offline fixtures for every MCP investigation tool.
os.environ["TG_MOCK_MODE"] = "true"

import pytest  # noqa: E402

from agent import models as am  # noqa: E402
from agent.investigator import (  # noqa: E402
    Investigator,
    LocalAdjudicator,
    MAX_GEMINI_STEPS,
    MCP_TOOLS,
    render_report,
)
from agent.models import InvestigationReport  # noqa: E402

EXPECTED_TOOLS = {
    "investigate_transaction",
    "trace_connected_entities",
    "detect_card_testing",
    "analyze_region_anomalies",
    "retrieve_similar_cases",
    "calculate_case_exposure",
    "validate_graph_metrics",
}


# ---------------------------------------------------------------------------
# 1. Imports / syntax
# ---------------------------------------------------------------------------


def test_import_all_agent_modules():
    for mod in ("agent", "agent.models", "agent.prompts", "agent.investigator"):
        importlib.import_module(mod)


def test_agent_reuses_all_seven_mcp_tools():
    assert set(MCP_TOOLS) == EXPECTED_TOOLS
    assert len(MCP_TOOLS) == 7


def test_prompts_are_well_formed():
    from agent import prompts as ap

    assert ap.SYSTEM_PROMPT
    assert "R1" in ap.SYSTEM_PROMPT and "R10" in ap.SYSTEM_PROMPT
    decl_names = {d["name"] for d in ap.FUNCTION_DECLARATIONS}
    assert decl_names == EXPECTED_TOOLS
    assert "3514030" in ap.build_start_prompt("3514030")


# ---------------------------------------------------------------------------
# 2. Mock end-to-end investigation (local engine, txn 3514030)
# ---------------------------------------------------------------------------


def test_local_end_to_end_3514030():
    report = LocalAdjudicator().investigate("3514030")

    assert isinstance(report, InvestigationReport)
    assert report.transaction_id == "3514030"
    assert report.engine == "local"

    # Structured evidence & signals were produced from the MCP tools.
    assert report.evidence, "expected evidence items"
    assert report.risk_signals, "expected risk signals"
    assert report.next_best_actions, "expected recommended actions"
    assert report.approval_route in ("auto", "L1", "L2")

    # The transaction/card evidence is present and grounded.
    types = [ev.type for ev in report.evidence]
    assert "TRANSACTION_RECORD" in types
    assert "CARD_INSTRUMENT" in types
    assert "CARD_TESTING_EVALUATION" in types
    assert "GEOGRAPHIC_DISPERSION" in types

    # Tool ledger is recorded and named after real MCP tools.
    assert report.tools_called
    for tool in report.tools_called:
        assert tool in EXPECTED_TOOLS

    # Guardrail: never fraud purely from a score.
    assert report.verdict in ("fraud", "legitimate", "uncertain")
    score_only = {s.signal for s in report.risk_signals} <= {
        "ELEVATED_MODEL_RISK_SCORE",
        "MODERATE_MODEL_RISK_SCORE",
    }
    if score_only:
        assert report.verdict != "fraud", "must not declare fraud from a model score alone"


def test_render_report_structure():
    report = LocalAdjudicator().investigate("3514030")
    text = render_report(report)

    assert "HHGOA AI INVESTIGATOR" in text
    assert "Transaction: 3514030" in text
    for section in (
        "INVESTIGATION SUMMARY",
        "EVIDENCE",
        "RISK SIGNALS",
        "RELATED ENTITIES",
        "HISTORICAL PRECEDENT",
        "UNCERTAINTY",
        "NEXT BEST ACTION",
        "APPROVAL ROUTE",
        "REASONING",
        "MCP TOOLS CALLED",
    ):
        assert section in text


# ---------------------------------------------------------------------------
# 3. Missing transaction
# ---------------------------------------------------------------------------


def test_missing_transaction_is_not_declared_fraud():
    report = LocalAdjudicator().investigate("999999")
    assert report.verdict in ("uncertain", "legitimate")
    assert any("ESCALATE_TO_ANALYST" == a.action for a in report.next_best_actions)
    assert report.uncertainty


# ---------------------------------------------------------------------------
# 4. Gemini function-calling loop (stubbed model, real MCP execution)
# ---------------------------------------------------------------------------

from google.genai import types as genai_types  # noqa: E402


class _FakeResponse:
    def __init__(self, text=None, function_calls=None):
        self.text = text
        self.function_calls = function_calls


class _FakeChat:
    """Replays a canned plan of function calls then a final JSON report."""

    def __init__(self, plan):
        self.plan = list(plan)
        self.sent_messages = []

    def send_message(self, message):
        self.sent_messages.append(message)
        assert self.plan, "model called tools beyond the canned plan"
        return self.plan.pop(0)


FINAL_JSON = """```json
{
  "summary": "Investigated txn 3514030. Moderate model score only, no corroborating evidence.",
  "verdict": "uncertain",
  "fraud_probability": 0.35,
  "next_best_actions": [
    {"action": "VERIFY_WITH_CUSTOMER", "route": "auto", "reason": "R1: single uncorroborated signal"},
    {"action": "STEP_UP_AUTH", "route": "auto", "reason": "R1: add independent confirmation"}
  ],
  "approval_route": "auto",
  "uncertainty": ["No customer reply available"],
  "reasoning": "Only the model risk score supports the alert; per Policy 0 a score is not a verdict."
}
```"""


def _build_gemini_agent_with_stub_plan():
    from agent.investigator import GeminiAgent

    agent = GeminiAgent(api_key="dummy-key-for-stub-test", model_name="fake-model")
    plan = [
        _FakeResponse(
            function_calls=[
                genai_types.FunctionCall(name="investigate_transaction", args={"txn_id": "3514030"})
            ]
        ),
        _FakeResponse(
            function_calls=[
                genai_types.FunctionCall(name="trace_connected_entities", args={"target_card_id": "C12382-K1"}),
                genai_types.FunctionCall(name="analyze_region_anomalies", args={"target_card_id": "C12382-K1"}),
                genai_types.FunctionCall(name="detect_card_testing", args={"target_card_id": "C12382-K1"}),
            ]
        ),
        _FakeResponse(
            function_calls=[
                genai_types.FunctionCall(name="retrieve_similar_cases", args={"customer_id": "C12382", "card_id": "C12382-K1"}),
                genai_types.FunctionCall(name="calculate_case_exposure", args={"target_case_id": "HHG-001"}),
            ]
        ),
        _FakeResponse(text=FINAL_JSON),
    ]
    agent._build_chat = lambda executor: _FakeChat(plan)  # type: ignore[method-assign]
    return agent


def test_gemini_loop_calls_mcp_tools_and_produces_report():
    agent = _build_gemini_agent_with_stub_plan()
    report = agent.investigate("3514030")

    assert report.engine == "gemini"
    assert report.evidence, "tool results must be aggregated into evidence"
    # Every MCP tool the model requested was actually executed.
    called = {call.tool for call in report.tool_calls}
    assert "investigate_transaction" in called
    assert called <= EXPECTED_TOOLS
    # Narrative came from the model's JSON.
    assert report.summary
    assert report.verdict == "uncertain"
    assert any(a.action == "VERIFY_WITH_CUSTOMER" for a in report.next_best_actions)
    assert report.approval_route == "auto"


def test_gemini_loop_never_exceeds_max_steps():
    agent = _build_gemini_agent_with_stub_plan()
    # A pathological model that keeps calling tools forever.
    plan = [
        _FakeResponse(function_calls=[genai_types.FunctionCall(name="validate_graph_metrics", args={})])
    ] * (MAX_GEMINI_STEPS + 5)
    plan.append(_FakeResponse(text=FINAL_JSON))
    agent._build_chat = lambda executor: _FakeChat(plan)  # type: ignore[method-assign]

    report = agent.investigate("3514030")
    assert report is not None
    assert len(report.tool_calls) <= MAX_GEMINI_STEPS


# ---------------------------------------------------------------------------
# 5. CLI entry points
# ---------------------------------------------------------------------------


def test_cli_plain_output(capsys):
    from agent.investigator import main as cli_main

    code = cli_main(["3514030"])
    out = capsys.readouterr().out
    assert code == 0
    assert "HHGOA AI INVESTIGATOR" in out
    assert "Transaction: 3514030" in out


def test_cli_json_output(capsys):
    from agent.investigator import main as cli_main

    code = cli_main(["3514030", "--json"])
    out = capsys.readouterr().out
    assert code == 0
    data = json.loads(out)
    assert data["transaction_id"] == "3514030"
    assert isinstance(data["evidence"], list)
    assert isinstance(data["next_best_actions"], list)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))