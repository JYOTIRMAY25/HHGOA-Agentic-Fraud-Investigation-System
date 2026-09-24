"""
HHGOA TigerGraph MCP Input Validation Module
Enforces strict parameter types, non-empty identifiers, bounds, and injection prevention.
"""

import re
from typing import Optional, Dict, Any

class ValidationError(Exception):
    """Raised when an input parameter violates schema or bounds."""
    def __init__(self, message: str, parameter: str):
        super().__init__(message)
        self.parameter = parameter

def validate_txn_id(txn_id: str) -> str:
    if not txn_id or not isinstance(txn_id, str):
        raise ValidationError("Transaction ID must be a non-empty string.", "txn_id")
    cleaned = txn_id.strip()
    if not re.match(r"^[0-9]{4,12}$", cleaned):
        raise ValidationError(f"Invalid transaction ID format '{txn_id}'. Expected numeric string.", "txn_id")
    return cleaned

def validate_card_id(card_id: str) -> str:
    if not card_id or not isinstance(card_id, str):
        raise ValidationError("Card ID must be a non-empty string.", "card_id")
    cleaned = card_id.strip()
    if not re.match(r"^C[0-9]{4,6}-K[1-9]$", cleaned):
        raise ValidationError(f"Invalid card ID format '{card_id}'. Expected 'CXXXXX-KX'.", "card_id")
    return cleaned

def validate_case_id(case_id: str) -> str:
    if not case_id or not isinstance(case_id, str):
        raise ValidationError("Case ID must be a non-empty string.", "case_id")
    cleaned = case_id.strip()
    if not re.match(r"^(HHG-[0-9]{3}|CC-[0-9]{4,5})$", cleaned):
        raise ValidationError(f"Invalid case ID format '{case_id}'. Expected 'HHG-XXX' or 'CC-XXXX'.", "case_id")
    return cleaned

def validate_hops(hops: Optional[int]) -> int:
    if hops is None:
        return 2
    if not isinstance(hops, int) or hops < 1 or hops > 3:
        raise ValidationError(f"max_hops must be an integer between 1 and 3, got '{hops}'.", "max_hops")
    return hops

def validate_window_minutes(window: Optional[int]) -> int:
    if window is None:
        return 60
    if not isinstance(window, int) or window < 10 or window > 1440:
        raise ValidationError(f"window_minutes must be between 10 and 1440, got '{window}'.", "window_minutes")
    return window

def validate_micro_threshold(threshold: Optional[float]) -> float:
    if threshold is None:
        return 5.0
    try:
        val = float(threshold)
    except (ValueError, TypeError):
        raise ValidationError(f"micro_threshold must be a valid float, got '{threshold}'.", "micro_threshold")
    if val < 0.5 or val > 50.0:
        raise ValidationError(f"micro_threshold must be between 0.5 and 50.0 USD, got '{val}'.", "micro_threshold")
    return val

def validate_min_attempts(attempts: Optional[int]) -> int:
    if attempts is None:
        return 3
    if not isinstance(attempts, int) or attempts < 1 or attempts > 10:
        raise ValidationError(f"min_micro_attempts must be between 1 and 10, got '{attempts}'.", "min_micro_attempts")
    return attempts

def validate_similar_cases_inputs(customer_id: Optional[str], card_id: Optional[str], pattern_id: Optional[str]) -> Dict[str, str]:
    cust = customer_id.strip() if customer_id else ""
    card = card_id.strip() if card_id else ""
    pat = pattern_id.strip() if pattern_id else ""

    if not cust and not card and not pat:
        raise ValidationError("At least one of customer_id, card_id, or pattern_id must be provided.", "search_keys")

    valid_patterns = {"card_testing", "card_not_present_fraud", "card_not_present_new_device", "out_of_region_use", "account_takeover", "undocumented", "none", ""}
    if pat and pat not in valid_patterns:
        raise ValidationError(f"Invalid pattern_id '{pat}'. Must be one of {sorted(valid_patterns - {''})}.", "pattern_id")

    return {"customer_id": cust, "card_id": card, "pattern_id": pat}
