"""
HHGOA TigerGraph MCP Output Normalizer
Transforms raw TigerGraph query outputs into structured, agent-ready investigation evidence.
"""

from typing import Dict, Any, List

class EvidenceNormalizer:

    @staticmethod
    def normalize_investigate_transaction(txn_id: str, raw_data: Any) -> Dict[str, Any]:
        """Normalizes output of investigate_transaction query."""
        evidence: List[Dict[str, Any]] = []
        relationships: List[Dict[str, Any]] = []
        risk_signals: List[Dict[str, Any]] = []

        # Parse TigerGraph output blocks
        txn_record = None
        card_record = None
        device_record = None
        p_emails = []
        r_emails = []
        regions = []
        cases = []

        if isinstance(raw_data, list):
            for block in raw_data:
                if isinstance(block, dict):
                    if "@@txn_details" in block and block["@@txn_details"]:
                        txn_record = block["@@txn_details"][0]
                    elif "@@card_details" in block and block["@@card_details"]:
                        card_record = block["@@card_details"][0]
                    elif "@@device_details" in block and block["@@device_details"]:
                        device_record = block["@@device_details"][0]
                    elif "@@purchaser_emails" in block:
                        p_emails = block["@@purchaser_emails"]
                    elif "@@recipient_emails" in block:
                        r_emails = block["@@recipient_emails"]
                    elif "@@billing_regions" in block:
                        regions = block["@@billing_regions"]
                    elif "@@prior_cases" in block:
                        cases = block["@@prior_cases"]

        if not txn_record:
            return {
                "error": True,
                "type": "ENTITY_NOT_FOUND",
                "message": f"Transaction '{txn_id}' was not found in the graph.",
                "target": txn_id
            }

        # Build primary transaction evidence
        evidence.append({
            "type": "TRANSACTION_RECORD",
            "entity": txn_record.get("transaction_id", txn_id),
            "relationship": "TARGET",
            "attributes": {
                "ts": txn_record.get("ts"),
                "amount": txn_record.get("amount"),
                "channel": txn_record.get("channel"),
                "product_cd": txn_record.get("product_cd"),
                "risk_score": txn_record.get("risk_score"),
                "is_flagged": txn_record.get("is_flagged", False)
            }
        })

        # Risk score signal
        rs = txn_record.get("risk_score", 0.0)
        if rs is not None and rs >= 0.70:
            risk_signals.append({
                "signal": "ELEVATED_MODEL_RISK_SCORE",
                "value": rs,
                "severity": "HIGH",
                "guidance": "Model score > 0.70 is an input reason to inspect, not a verdict (README line 36/91)"
            })
        elif rs is not None and rs >= 0.40:
            risk_signals.append({
                "signal": "MODERATE_MODEL_RISK_SCORE",
                "value": rs,
                "severity": "MEDIUM",
                "guidance": "Requires correlation with device and regional history"
            })

        # Card & Customer evidence
        if card_record:
            c_id = card_record.get("card_id")
            cust_id = card_record.get("customer_id")
            evidence.append({
                "type": "CARD_INSTRUMENT",
                "entity": c_id,
                "relationship": "PERFORMED_BY",
                "attributes": {
                    "customer_id": cust_id,
                    "network": card_record.get("network"),
                    "card_type": card_record.get("card_type")
                }
            })
            relationships.append({"source": txn_id, "edge": "PERFORMED_BY", "target": c_id})
            if cust_id:
                relationships.append({"source": c_id, "edge": "OWNED_BY", "target": cust_id})

        # Device evidence
        if device_record:
            d_id = device_record.get("device_profile_id")
            evidence.append({
                "type": "DEVICE_PROFILE",
                "entity": d_id,
                "relationship": "USED_DEVICE",
                "attributes": {
                    "device_info": device_record.get("device_info"),
                    "device_type": device_record.get("device_type"),
                    "os": device_record.get("os"),
                    "browser": device_record.get("browser"),
                    "device_status": device_record.get("device_status"),
                    "proxy_flag": device_record.get("proxy_flag")
                }
            })
            relationships.append({"source": txn_id, "edge": "USED_DEVICE", "target": d_id})
            if device_record.get("device_status") == "New":
                risk_signals.append({
                    "signal": "NEW_DEVICE_IDENTIFIED",
                    "severity": "MEDIUM",
                    "guidance": "Device marked New on this account (Pattern 3 / Rule R3)"
                })
            if "ANONYMOUS" in str(device_record.get("proxy_flag", "")):
                risk_signals.append({
                    "signal": "ANONYMOUS_PROXY_DETECTED",
                    "severity": "HIGH",
                    "guidance": "Transaction originated behind anonymous proxy"
                })

        # Regions and emails
        for reg in regions:
            evidence.append({
                "type": "BILLING_REGION",
                "entity": reg,
                "relationship": "BILLED_IN",
                "attributes": {"region_id": reg}
            })
            relationships.append({"source": txn_id, "edge": "BILLED_IN", "target": reg})

        for em in p_emails:
            evidence.append({
                "type": "PURCHASER_EMAIL",
                "entity": em,
                "relationship": "PURCHASER_EMAIL",
                "attributes": {"domain": em}
            })
            relationships.append({"source": txn_id, "edge": "PURCHASER_EMAIL", "target": em})

        for em in r_emails:
            evidence.append({
                "type": "RECIPIENT_EMAIL",
                "entity": em,
                "relationship": "RECIPIENT_EMAIL",
                "attributes": {"domain": em}
            })
            relationships.append({"source": txn_id, "edge": "RECIPIENT_EMAIL", "target": em})

        for c_id in cases:
            evidence.append({
                "type": "ASSOCIATED_CASE",
                "entity": c_id,
                "relationship": "INVOLVED_IN_CASE",
                "attributes": {"case_id": c_id}
            })
            relationships.append({"source": txn_id, "edge": "INVOLVED_IN_CASE", "target": c_id})

        return {
            "investigation": {
                "target": txn_id,
                "target_type": "Transaction"
            },
            "evidence": evidence,
            "relationships": relationships,
            "risk_signals": risk_signals,
            "metadata": {
                "query": "investigate_transaction",
                "channel": txn_record.get("channel"),
                "is_flagged": txn_record.get("is_flagged", False)
            }
        }

    @staticmethod
    def normalize_trace_connected_entities(card_id: str, raw_data: Any) -> Dict[str, Any]:
        """Normalizes output of trace_connected_entities query."""
        evidence = []
        relationships = []
        risk_signals = []
        connected_cards = 0
        shared_devices = 0

        if isinstance(raw_data, list):
            for block in raw_data:
                if "@@results" in block:
                    for item in block["@@results"]:
                        e_type = item.get("entity_type")
                        e_id = item.get("entity_id")
                        c_path = item.get("connection_path")
                        hop = item.get("hop_distance")

                        evidence.append({
                            "type": e_type,
                            "entity": e_id,
                            "relationship": c_path,
                            "attributes": {"hop_distance": hop}
                        })
                        relationships.append({
                            "source": card_id,
                            "edge": c_path,
                            "target": e_id
                        })
                if "total_connected_cards" in block:
                    connected_cards = block["total_connected_cards"]
                if "total_shared_devices" in block:
                    shared_devices = block["total_shared_devices"]

        # Risk signal evaluation
        if any(e["relationship"] == "SHARED_DEVICE_SYNDICATE" for e in evidence):
            risk_signals.append({
                "signal": "CROSS_ACCOUNT_DEVICE_SHARING",
                "severity": "CRITICAL",
                "policy_rule": "R6",
                "guidance": "Device shared across disparate customer cards. Rule R6 calls for CREATE_CASE, FILE_REPORT, and MONITOR_CONNECTED_CARDS."
            })

        return {
            "investigation": {
                "target": card_id,
                "target_type": "Card"
            },
            "evidence": evidence,
            "relationships": relationships,
            "risk_signals": risk_signals,
            "metadata": {
                "query": "trace_connected_entities",
                "total_connected_cards": connected_cards,
                "total_shared_devices": shared_devices
            }
        }

    @staticmethod
    def normalize_detect_card_testing(card_id: str, raw_data: Any) -> Dict[str, Any]:
        """Normalizes output of detect_card_testing query."""
        is_detected = False
        micro_count = 0
        large_charge = 0.0
        sequence = []

        if isinstance(raw_data, list):
            for block in raw_data:
                if "is_card_testing_detected" in block:
                    is_detected = bool(block["is_card_testing_detected"])
                if "micro_authorization_count" in block:
                    micro_count = block["micro_authorization_count"]
                if "subsequent_large_charge" in block:
                    large_charge = float(block["subsequent_large_charge"])
                if "sequence" in block:
                    sequence = block["sequence"]

        evidence = [{
            "type": "CARD_TESTING_EVALUATION",
            "entity": card_id,
            "relationship": "SEQUENCE_ANALYSIS",
            "attributes": {
                "is_detected": is_detected,
                "micro_authorization_count": micro_count,
                "subsequent_large_charge": large_charge,
                "sequence_length": len(sequence)
            }
        }]

        risk_signals = []
        if is_detected:
            risk_signals.append({
                "signal": "CARD_TESTING_BURST_CONFIRMED",
                "severity": "CRITICAL",
                "policy_rule": "R5",
                "guidance": "Three or more micro authorizations followed by larger purchase. Prescribed: DECLINE_TRANSACTION and STEP_UP_AUTH. If purchase > $100 cleared: BLOCK_CARD."
            })

        return {
            "investigation": {
                "target": card_id,
                "target_type": "Card"
            },
            "evidence": evidence,
            "relationships": [],
            "risk_signals": risk_signals,
            "metadata": {
                "query": "detect_card_testing",
                "micro_count": micro_count,
                "sequence_sample": sequence[:5]
            }
        }

    @staticmethod
    def normalize_analyze_region_anomalies(card_id: str, raw_data: Any) -> Dict[str, Any]:
        """Normalizes output of analyze_region_anomalies query."""
        total_txns = 0
        distribution = {}
        foreign_txns = 0

        if isinstance(raw_data, list):
            for block in raw_data:
                if "total_transactions" in block:
                    total_txns = block["total_transactions"]
                if "region_distribution" in block:
                    distribution = block["region_distribution"]
                if "international_transaction_count" in block:
                    foreign_txns = block["international_transaction_count"]

        evidence = [{
            "type": "GEOGRAPHIC_DISPERSION",
            "entity": card_id,
            "relationship": "REGIONAL_FOOTPRINT",
            "attributes": {
                "total_transactions": total_txns,
                "distinct_regions": len(distribution),
                "foreign_transaction_count": foreign_txns,
                "region_distribution": distribution
            }
        }]

        risk_signals = []
        if foreign_txns > 0:
            risk_signals.append({
                "signal": "INTERNATIONAL_OUT_OF_REGION_USE",
                "severity": "HIGH",
                "guidance": "Card has transactions billed outside domestic jurisdiction (addr2 != 87.0)"
            })
        if len(distribution) > 1:
            risk_signals.append({
                "signal": "MULTI_REGION_ACTIVITY",
                "severity": "MEDIUM",
                "guidance": "Card observed in multiple distinct billing regions. Distinguish sustained trip from clone (README line 119)"
            })

        return {
            "investigation": {
                "target": card_id,
                "target_type": "Card"
            },
            "evidence": evidence,
            "relationships": [],
            "risk_signals": risk_signals,
            "metadata": {
                "query": "analyze_region_anomalies",
                "dominant_region": max(distribution, key=distribution.get) if distribution else None
            }
        }

    @staticmethod
    def normalize_retrieve_similar_cases(target_id: str, raw_data: Any) -> Dict[str, Any]:
        """Normalizes output of retrieve_similar_cases query."""
        precedents = []
        if isinstance(raw_data, list):
            for block in raw_data:
                if "similar_cases" in block:
                    for case in block["similar_cases"]:
                        precedents.append({
                            "case_id": case.get("case_id"),
                            "status": case.get("status"),
                            "outcome": case.get("outcome"),
                            "pattern": case.get("pattern"),
                            "exposure_usd": case.get("exposure_usd"),
                            "report_filed": case.get("report_filed"),
                            "actions_taken": case.get("actions_taken"),
                            "analyst_notes": case.get("analyst_notes"),
                            "match_reason": case.get("match_reason")
                        })

        evidence = []
        for p in precedents:
            evidence.append({
                "type": "HISTORICAL_CASE_PRECEDENT",
                "entity": p["case_id"],
                "relationship": p["match_reason"],
                "attributes": {
                    "outcome": p["outcome"],
                    "pattern": p["pattern"],
                    "exposure_usd": p["exposure_usd"],
                    "report_filed": p["report_filed"],
                    "actions_taken": p["actions_taken"],
                    "analyst_notes": p["analyst_notes"]
                }
            })

        return {
            "investigation": {
                "target": target_id,
                "target_type": "InvestigationSubject"
            },
            "evidence": evidence,
            "relationships": [],
            "risk_signals": [],
            "metadata": {
                "query": "retrieve_similar_cases",
                "precedent_count": len(precedents)
            }
        }

    @staticmethod
    def normalize_calculate_case_exposure(case_id: str, raw_data: Any) -> Dict[str, Any]:
        """Normalizes output of calculate_case_exposure query."""
        total_exposure = 0.0
        fraud_count = 0
        txn_ids = []
        approval_route = "auto"

        if isinstance(raw_data, list):
            for block in raw_data:
                if "total_exposure_usd" in block:
                    total_exposure = float(block["total_exposure_usd"])
                if "fraud_transaction_count" in block:
                    fraud_count = block["fraud_transaction_count"]
                if "transaction_ids" in block:
                    txn_ids = block["transaction_ids"]
                if "required_approval_route" in block:
                    approval_route = block["required_approval_route"]

        evidence = [{
            "type": "EXPOSURE_AGGREGATION",
            "entity": case_id,
            "relationship": "CASE_FINANCIAL_IMPACT",
            "attributes": {
                "total_exposure_usd": total_exposure,
                "fraud_transaction_count": fraud_count,
                "transaction_ids": txn_ids,
                "required_approval_route": approval_route
            }
        }]

        risk_signals = []
        if total_exposure > 2500.0:
            risk_signals.append({
                "signal": "HIGH_EXPOSURE_THRESHOLD_EXCEEDED",
                "severity": "CRITICAL",
                "guidance": "Exposure > $2,500 requires Fraud Manager (L2) approval for card blocking (Policy Section 2)"
            })
        elif total_exposure > 1000.0:
            risk_signals.append({
                "signal": "SAR_FILING_THRESHOLD_REACHED",
                "severity": "HIGH",
                "guidance": "Exposure > $1,000 mandates FILE_REPORT if fraud is confirmed (Policy Rule R2 / Section 3a)"
            })

        return {
            "investigation": {
                "target": case_id,
                "target_type": "FraudCase"
            },
            "evidence": evidence,
            "relationships": [],
            "risk_signals": risk_signals,
            "metadata": {
                "query": "calculate_case_exposure",
                "total_exposure_usd": total_exposure,
                "required_approval_route": approval_route
            }
        }

    @staticmethod
    def normalize_validate_graph_metrics(raw_data: Any) -> Dict[str, Any]:
        """Normalizes output of validate_graph_metrics query."""
        metrics = {}
        if isinstance(raw_data, list):
            for block in raw_data:
                if isinstance(block, dict):
                    metrics.update(block)

        evidence = [{
            "type": "GRAPH_METRICS",
            "entity": "HHGOA_Fraud_Graph",
            "relationship": "VALIDATION_SNAPSHOT",
            "attributes": metrics
        }]

        return {
            "investigation": {
                "target": "HHGOA_Fraud_Graph",
                "target_type": "Graph"
            },
            "evidence": evidence,
            "relationships": [],
            "risk_signals": [],
            "metadata": {
                "query": "validate_graph_metrics",
                **metrics
            }
        }
