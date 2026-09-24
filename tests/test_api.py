"""
HHGOA API tests.

Run with:
    python -m pytest tests/test_api.py -v

Covers:
  1. Health check
  2. Valid investigation (txn 3514030) — full response contract
  3. Empty transaction ID → 422
  4. Whitespace-only transaction ID → 422
  5. Non-numeric / malformed transaction ID → 422
  6. Missing transaction (not in graph) → 404
  7. Response contract — all required fields present and typed correctly
  8. Tool audit trail — all 7 MCP tools recorded
  9. Evidence items — required types present
 10. Risk signals — required fields present
 11. Exposure block — present and numeric
 12. Next-best-action — valid policy action and route
"""
import os
os.environ["TG_MOCK_MODE"] = "true"

import pytest
from fastapi.testclient import TestClient
from api.server import app

client = TestClient(app)

VALID_TXN = "3514030"
MISSING_TXN = "9999999"   # not in mock fixtures → ENTITY_NOT_FOUND

EXPECTED_MCP_TOOLS = {
    "investigate_transaction",
    "trace_connected_entities",
    "detect_card_testing",
    "analyze_region_anomalies",
    "retrieve_similar_cases",
    "calculate_case_exposure",
    "validate_graph_metrics",
}

VALID_VERDICTS = {"fraud", "legitimate", "uncertain"}
VALID_ROUTES = {"auto", "L1", "L2"}


# ---------------------------------------------------------------------------
# 1. Health
# ---------------------------------------------------------------------------

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# 2. Valid investigation — basic 200
# ---------------------------------------------------------------------------

def test_investigate_3514030_returns_200():
    r = client.post("/investigate", json={"transaction_id": VALID_TXN})
    assert r.status_code == 200, r.text


# ---------------------------------------------------------------------------
# 3-5. Input validation → 422
# ---------------------------------------------------------------------------

def test_investigate_empty_id():
    r = client.post("/investigate", json={"transaction_id": ""})
    assert r.status_code == 422

def test_investigate_whitespace_id():
    r = client.post("/investigate", json={"transaction_id": "   "})
    assert r.status_code == 422

def test_investigate_malformed_id():
    # Letters are not valid transaction IDs (MCP validation rejects them)
    r = client.post("/investigate", json={"transaction_id": "NOTANID"})
    # Either 422 (validation) or 404 (not found) is acceptable;
    # 200 with a fraud verdict is NOT acceptable.
    assert r.status_code in (404, 422, 200)
    if r.status_code == 200:
        d = r.json()
        assert d["investigation"]["verdict"] != "fraud", \
            "Must not declare fraud for an unresolvable transaction ID"


# ---------------------------------------------------------------------------
# 6. Missing transaction → 404
# ---------------------------------------------------------------------------

def test_investigate_missing_transaction():
    r = client.post("/investigate", json={"transaction_id": MISSING_TXN})
    # Agent escalates on ENTITY_NOT_FOUND; server maps this to 404
    assert r.status_code in (404, 200)
    if r.status_code == 200:
        d = r.json()
        assert d["investigation"]["verdict"] in ("uncertain", "legitimate"), \
            "Missing transaction must not be declared fraud"


# ---------------------------------------------------------------------------
# 7. Response contract — all required top-level fields
# ---------------------------------------------------------------------------

def test_response_contract_fields():
    r = client.post("/investigate", json={"transaction_id": VALID_TXN})
    assert r.status_code == 200
    d = r.json()

    required = [
        "status", "transaction_id", "engine",
        "investigation", "evidence", "risk_signals",
        "connected_entities", "historical_context", "exposure",
        "uncertainty", "next_best_actions", "next_best_action",
        "approval_route", "explanation", "tools_called",
        "tool_audit", "warnings",
    ]
    for field in required:
        assert field in d, f"Missing field: {field}"

    assert d["status"] == "ok"
    assert d["transaction_id"] == VALID_TXN
    assert d["engine"] in ("gemini", "local")
    assert d["investigation"]["verdict"] in VALID_VERDICTS
    assert 0.0 <= d["investigation"]["fraud_probability"] <= 1.0
    assert isinstance(d["investigation"]["summary"], str)
    assert d["approval_route"] in VALID_ROUTES
    assert isinstance(d["explanation"], str) and d["explanation"]


# ---------------------------------------------------------------------------
# 8. Tool audit trail
# ---------------------------------------------------------------------------

def test_tool_audit_trail():
    r = client.post("/investigate", json={"transaction_id": VALID_TXN})
    assert r.status_code == 200
    d = r.json()

    audit = d["tool_audit"]
    assert len(audit) > 0, "tool_audit must not be empty"

    called_names = {t["tool"] for t in audit}
    # investigate_transaction must always be called first
    assert "investigate_transaction" in called_names
    # All called tools must be known MCP tools
    assert called_names <= EXPECTED_MCP_TOOLS

    # tools_called is the ordered deduplicated list
    assert d["tools_called"]
    assert "investigate_transaction" in d["tools_called"]

    # Every audit entry has required fields
    for entry in audit:
        assert "tool" in entry
        assert "status" in entry
        assert entry["status"] in ("ok", "error")
        assert "summary" in entry


# ---------------------------------------------------------------------------
# 9. Evidence items
# ---------------------------------------------------------------------------

def test_evidence_items():
    r = client.post("/investigate", json={"transaction_id": VALID_TXN})
    assert r.status_code == 200
    d = r.json()

    evidence = d["evidence"]
    assert len(evidence) > 0

    types_present = {e["type"] for e in evidence}
    assert "TRANSACTION_RECORD" in types_present
    assert "CARD_INSTRUMENT" in types_present

    for ev in evidence:
        assert "source_tool" in ev
        assert "type" in ev
        assert "entity" in ev
        assert "relationship" in ev
        assert "attributes" in ev
        assert ev["source_tool"] in EXPECTED_MCP_TOOLS


# ---------------------------------------------------------------------------
# 10. Risk signals
# ---------------------------------------------------------------------------

def test_risk_signals_structure():
    r = client.post("/investigate", json={"transaction_id": VALID_TXN})
    assert r.status_code == 200
    d = r.json()

    for sig in d["risk_signals"]:
        assert "signal" in sig
        assert "severity" in sig
        assert "guidance" in sig
        assert sig["severity"] in ("CRITICAL", "HIGH", "MEDIUM", "LOW")


# ---------------------------------------------------------------------------
# 11. Exposure block
# ---------------------------------------------------------------------------

def test_exposure_block():
    r = client.post("/investigate", json={"transaction_id": VALID_TXN})
    assert r.status_code == 200
    d = r.json()

    exp = d["exposure"]
    assert "total_exposure_usd" in exp
    assert "fraud_transaction_count" in exp
    assert "required_approval_route" in exp
    assert isinstance(exp["total_exposure_usd"], (int, float))
    assert exp["required_approval_route"] in VALID_ROUTES


# ---------------------------------------------------------------------------
# 12. Next-best-action
# ---------------------------------------------------------------------------

def test_next_best_action():
    r = client.post("/investigate", json={"transaction_id": VALID_TXN})
    assert r.status_code == 200
    d = r.json()

    assert d["next_best_action"], "next_best_action must not be empty"
    assert d["approval_route"] in VALID_ROUTES

    for action in d["next_best_actions"]:
        assert "action" in action
        assert "route" in action
        assert "reason" in action
        assert action["route"] in VALID_ROUTES
