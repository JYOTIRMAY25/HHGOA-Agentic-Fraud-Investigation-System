"""
HHGOA TigerGraph Investigation Tool Implementations
Wraps existing GSQL queries with strict validation, connection execution, and output normalization.
"""

from typing import Dict, Any, Optional
from mcp.tools.validation import (
    ValidationError,
    validate_txn_id,
    validate_card_id,
    validate_case_id,
    validate_hops,
    validate_window_minutes,
    validate_micro_threshold,
    validate_min_attempts,
    validate_similar_cases_inputs
)
from mcp.connection import default_connection, TigerGraphConnectionError
from mcp.normalizer import EvidenceNormalizer


def execute_validate_graph_metrics(conn=None) -> Dict[str, Any]:
    """MCP Tool: validate_graph_metrics"""
    conn = conn or default_connection
    try:
        raw_result = conn.run_installed_query_sync("validate_graph_metrics", {})
        return EvidenceNormalizer.normalize_validate_graph_metrics(raw_result)
    except TigerGraphConnectionError as e:
        return {"error": True, "type": "CONNECTION_FAILURE", "message": str(e)}
    except Exception as e:
        return {"error": True, "type": "QUERY_ERROR", "message": f"Unexpected execution error: {str(e)}"}


def execute_investigate_transaction(txn_id: str, conn=None) -> Dict[str, Any]:
    """MCP Tool: investigate_transaction"""
    try:
        clean_txn_id = validate_txn_id(txn_id)
    except ValidationError as e:
        return {"error": True, "type": "INVALID_PARAMETER", "parameter": e.parameter, "message": str(e), "target": txn_id}

    conn = conn or default_connection
    try:
        raw_result = conn.run_installed_query_sync("investigate_transaction", {"txn_id": clean_txn_id})
        return EvidenceNormalizer.normalize_investigate_transaction(clean_txn_id, raw_result)
    except TigerGraphConnectionError as e:
        return {"error": True, "type": "CONNECTION_FAILURE", "message": str(e), "target": clean_txn_id}
    except Exception as e:
        return {"error": True, "type": "QUERY_ERROR", "message": f"Unexpected execution error: {str(e)}", "target": clean_txn_id}

def execute_trace_connected_entities(target_card_id: str, max_hops: Optional[int] = 2, conn=None) -> Dict[str, Any]:
    """MCP Tool: trace_connected_entities"""
    try:
        clean_card_id = validate_card_id(target_card_id)
        clean_hops = validate_hops(max_hops)
    except ValidationError as e:
        return {"error": True, "type": "INVALID_PARAMETER", "parameter": e.parameter, "message": str(e), "target": target_card_id}

    conn = conn or default_connection
    try:
        raw_result = conn.run_installed_query_sync("trace_connected_entities", {"target_card_id": clean_card_id, "max_hops": clean_hops})
        return EvidenceNormalizer.normalize_trace_connected_entities(clean_card_id, raw_result)
    except TigerGraphConnectionError as e:
        return {"error": True, "type": "CONNECTION_FAILURE", "message": str(e), "target": clean_card_id}
    except Exception as e:
        return {"error": True, "type": "QUERY_ERROR", "message": f"Unexpected execution error: {str(e)}", "target": clean_card_id}

def execute_detect_card_testing(
    target_card_id: str,
    window_minutes: Optional[int] = 60,
    micro_threshold: Optional[float] = 5.0,
    min_micro_attempts: Optional[int] = 3,
    conn=None
) -> Dict[str, Any]:
    """MCP Tool: detect_card_testing"""
    try:
        clean_card_id = validate_card_id(target_card_id)
        clean_window = validate_window_minutes(window_minutes)
        clean_threshold = validate_micro_threshold(micro_threshold)
        clean_min_attempts = validate_min_attempts(min_micro_attempts)
    except ValidationError as e:
        return {"error": True, "type": "INVALID_PARAMETER", "parameter": e.parameter, "message": str(e), "target": target_card_id}

    conn = conn or default_connection
    try:
        raw_result = conn.run_installed_query_sync("detect_card_testing", {
            "target_card_id": clean_card_id,
            "window_minutes": clean_window,
            "micro_threshold": clean_threshold,
            "min_micro_attempts": clean_min_attempts
        })
        return EvidenceNormalizer.normalize_detect_card_testing(clean_card_id, raw_result)
    except TigerGraphConnectionError as e:
        return {"error": True, "type": "CONNECTION_FAILURE", "message": str(e), "target": clean_card_id}
    except Exception as e:
        return {"error": True, "type": "QUERY_ERROR", "message": f"Unexpected execution error: {str(e)}", "target": clean_card_id}

def execute_analyze_region_anomalies(target_card_id: str, conn=None) -> Dict[str, Any]:
    """MCP Tool: analyze_region_anomalies"""
    try:
        clean_card_id = validate_card_id(target_card_id)
    except ValidationError as e:
        return {"error": True, "type": "INVALID_PARAMETER", "parameter": e.parameter, "message": str(e), "target": target_card_id}

    conn = conn or default_connection
    try:
        raw_result = conn.run_installed_query_sync("analyze_region_anomalies", {"target_card_id": clean_card_id})
        return EvidenceNormalizer.normalize_analyze_region_anomalies(clean_card_id, raw_result)
    except TigerGraphConnectionError as e:
        return {"error": True, "type": "CONNECTION_FAILURE", "message": str(e), "target": clean_card_id}
    except Exception as e:
        return {"error": True, "type": "QUERY_ERROR", "message": f"Unexpected execution error: {str(e)}", "target": clean_card_id}

def execute_retrieve_similar_cases(
    customer_id: Optional[str] = "",
    card_id: Optional[str] = "",
    pattern_id: Optional[str] = "",
    conn=None
) -> Dict[str, Any]:
    """MCP Tool: retrieve_similar_cases"""
    try:
        clean_inputs = validate_similar_cases_inputs(customer_id, card_id, pattern_id)
    except ValidationError as e:
        return {"error": True, "type": "INVALID_PARAMETER", "parameter": e.parameter, "message": str(e), "target": customer_id or card_id or pattern_id}

    conn = conn or default_connection
    target_id = clean_inputs["customer_id"] or clean_inputs["card_id"] or clean_inputs["pattern_id"]
    try:
        raw_result = conn.run_installed_query_sync("retrieve_similar_cases", clean_inputs)
        return EvidenceNormalizer.normalize_retrieve_similar_cases(target_id, raw_result)
    except TigerGraphConnectionError as e:
        return {"error": True, "type": "CONNECTION_FAILURE", "message": str(e), "target": target_id}
    except Exception as e:
        return {"error": True, "type": "QUERY_ERROR", "message": f"Unexpected execution error: {str(e)}", "target": target_id}

def execute_calculate_case_exposure(target_case_id: str, conn=None) -> Dict[str, Any]:
    """MCP Tool: calculate_case_exposure"""
    try:
        clean_case_id = validate_case_id(target_case_id)
    except ValidationError as e:
        return {"error": True, "type": "INVALID_PARAMETER", "parameter": e.parameter, "message": str(e), "target": target_case_id}

    conn = conn or default_connection
    try:
        raw_result = conn.run_installed_query_sync("calculate_case_exposure", {"target_case_id": clean_case_id})
        return EvidenceNormalizer.normalize_calculate_case_exposure(clean_case_id, raw_result)
    except TigerGraphConnectionError as e:
        return {"error": True, "type": "CONNECTION_FAILURE", "message": str(e), "target": clean_case_id}
    except Exception as e:
        return {"error": True, "type": "QUERY_ERROR", "message": f"Unexpected execution error: {str(e)}", "target": clean_case_id}
