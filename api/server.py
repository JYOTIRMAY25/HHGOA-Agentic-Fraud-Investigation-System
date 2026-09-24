"""
HHGOA FastAPI backend.

Thin HTTP layer around agent/investigator.py.  All investigation logic lives
in the agent and MCP layers; this module handles only:
  - request validation
  - logging
  - error translation
  - response serialisation against the stable InvestigationResponse contract

Secrets (GEMINI_API_KEY, TigerGraph credentials) are never logged.
"""
from __future__ import annotations

import logging
import os
import time
import uuid
from dataclasses import asdict
from typing import Any, Dict

os.environ.setdefault("TG_MOCK_MODE", "true")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from api.models import (
    ErrorResponse,
    ExposureSummary,
    InvestigationResponse,
    InvestigationSummary,
    EvidenceItem,
    NextBestAction,
    RiskSignal,
    ToolCallRecord,
)

# ---------------------------------------------------------------------------
# Logging — never emit credentials or secrets
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("hhgoa.api")

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="HHGOA Fraud Investigation API",
    version="1.1.0",
    description=(
        "Agentic fraud investigation backed by TigerGraph MCP tools and Gemini. "
        "All risk signals are investigation inputs, never automatic verdicts."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://hhgoa-agentic-fraud-investigation-system-xtz7.onrender.com",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------
class InvestigateRequest(BaseModel):
    transaction_id: str

    @field_validator("transaction_id")
    @classmethod
    def must_be_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("transaction_id must be a non-empty string")
        return v.strip()


# ---------------------------------------------------------------------------
# Error codes
# ---------------------------------------------------------------------------
_ERROR_CODES: Dict[str, int] = {
    "INVALID_TRANSACTION_ID": 422,
    "TRANSACTION_NOT_FOUND": 404,
    "INVALID_PARAMETER": 422,
    "CONNECTION_FAILURE": 503,
    "QUERY_ERROR": 502,
    "INTERNAL_ERROR": 500,
}


def _error_response(code: str, message: str, txn_id: str | None = None) -> JSONResponse:
    status_code = _ERROR_CODES.get(code, 500)
    body = ErrorResponse(error_code=code, message=message, transaction_id=txn_id)
    logger.warning("Investigation error [%s] txn=%s: %s", code, txn_id, message)
    return JSONResponse(status_code=status_code, content=body.model_dump())


# ---------------------------------------------------------------------------
# Response builder — converts InvestigationReport → InvestigationResponse
# ---------------------------------------------------------------------------
def _build_response(report: Any) -> InvestigationResponse:
    """
    Serialise an agent InvestigationReport into the stable API contract.
    Extracts the ExposureSummary from EXPOSURE_AGGREGATION evidence items.
    """
    evidence = [EvidenceItem(**asdict(e)) for e in report.evidence]
    signals = [RiskSignal(**asdict(s)) for s in report.risk_signals]
    actions = [NextBestAction(**asdict(a)) for a in report.next_best_actions]
    audit = [ToolCallRecord(**asdict(t)) for t in report.tool_calls]

    # Extract exposure from evidence produced by calculate_case_exposure
    exposure = ExposureSummary()
    for ev in report.evidence:
        if ev.type == "EXPOSURE_AGGREGATION":
            attr = ev.attributes or {}
            exposure = ExposureSummary(
                total_exposure_usd=float(attr.get("total_exposure_usd") or 0.0),
                fraud_transaction_count=int(attr.get("fraud_transaction_count") or 0),
                required_approval_route=str(attr.get("required_approval_route") or "auto"),
            )
            break

    return InvestigationResponse(
        status="ok",
        transaction_id=report.transaction_id,
        engine=report.engine,
        investigation=InvestigationSummary(
            verdict=report.verdict,
            fraud_probability=report.fraud_probability,
            summary=report.summary,
        ),
        evidence=evidence,
        risk_signals=signals,
        connected_entities=report.related_entities,
        historical_context=report.historical_precedent,
        exposure=exposure,
        uncertainty=report.uncertainty,
        next_best_actions=actions,
        next_best_action=actions[0].action if actions else "CLOSE_NO_FRAUD",
        approval_route=report.approval_route,
        explanation=report.reasoning,
        tools_called=report.tools_called,
        tool_audit=audit,
        warnings=report.warnings,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


@app.post(
    "/investigate",
    response_model=InvestigationResponse,
    summary="Run an autonomous fraud investigation on a transaction",
    responses={
        200: {"description": "Investigation completed"},
        404: {"model": ErrorResponse, "description": "Transaction not found"},
        422: {"model": ErrorResponse, "description": "Invalid transaction ID"},
        500: {"model": ErrorResponse, "description": "Internal error"},
        502: {"model": ErrorResponse, "description": "Graph query error"},
        503: {"model": ErrorResponse, "description": "TigerGraph unreachable"},
    },
)
def investigate(req: InvestigateRequest, request: Request):
    request_id = str(uuid.uuid4())[:8]
    txn_id = req.transaction_id
    t0 = time.perf_counter()

    logger.info("[%s] Investigation started txn=%s", request_id, txn_id)

    # Import here so TG_MOCK_MODE is already set before the agent stack loads
    from agent.investigator import Investigator

    try:
        investigator = Investigator()
        logger.info("[%s] Engine selected: %s", request_id, investigator.engine)

        report = investigator.investigate(txn_id)

        elapsed = time.perf_counter() - t0
        logger.info(
            "[%s] Investigation complete txn=%s verdict=%s tools=%d evidence=%d elapsed=%.2fs",
            request_id,
            txn_id,
            report.verdict,
            len(report.tool_calls),
            len(report.evidence),
            elapsed,
        )

        # Surface a transaction-not-found as a 404 rather than a 200 with
        # an empty investigation — the agent sets verdict=uncertain and
        # escalates when the primary tool returns ENTITY_NOT_FOUND.
        primary_failed = any(
            c.status == "error" and "ENTITY_NOT_FOUND" in c.summary
            for c in report.tool_calls
        )
        if primary_failed:
            return _error_response(
                "TRANSACTION_NOT_FOUND",
                f"Transaction '{txn_id}' was not found in the graph.",
                txn_id,
            )

        return _build_response(report)

    except Exception as exc:
        elapsed = time.perf_counter() - t0
        # Log the exception type and message only — never the full traceback
        # in production, and never any credential values.
        logger.error(
            "[%s] Unexpected error txn=%s type=%s elapsed=%.2fs",
            request_id,
            txn_id,
            type(exc).__name__,
            elapsed,
        )
        return _error_response(
            "INTERNAL_ERROR",
            "An unexpected error occurred during investigation. "
            "Check server logs for details.",
            txn_id,
        )


# ---------------------------------------------------------------------------
# Entry point: python -m api.server
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
