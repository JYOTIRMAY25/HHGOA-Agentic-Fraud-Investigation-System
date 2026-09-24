# HHGOA TigerGraph MCP Tool Specification
**Formal Interface Definitions for Autonomous Fraud Investigation Agent**

---

## 1. Tool Selection & Summary Matrix

| MCP Tool | Purpose | Input | TigerGraph Query Invoked | Normalized Output |
|---|---|---|---|---|
| `investigate_transaction` | 360° context gathering for a flagged transaction | `txn_id` (STRING) | `investigate_transaction(txn_id)` | Structured transaction details, cardholder, device profile, email domains, billing region, and prior cases |
| `trace_connected_entities` | Multi-hop shared device & card syndicate discovery | `target_card_id` (STRING), `max_hops` (INT, opt) | `trace_connected_entities(target_card_id, max_hops)` | Sibling cards under same customer, shared devices, and cross-customer cards sharing attacker devices |
| `detect_card_testing` | Sequence analysis of micro-authorizations | `target_card_id` (STRING), `window_minutes` (INT, opt), `micro_threshold` (FLOAT, opt), `min_micro_attempts` (INT, opt) | `detect_card_testing(target_card_id, window_minutes, micro_threshold, min_micro_attempts)` | Micro-charge count, cash-out amount, velocity timestamps, testing detected flag |
| `analyze_region_anomalies` | Geographic card dispersion & travel validation | `target_card_id` (STRING) | `analyze_region_anomalies(target_card_id)` | Domestic vs foreign breakdown, region distribution map, out-of-region anomaly flags |
| `retrieve_similar_cases` | Case memory & precedent retrieval for GraphRAG | `customer_id` (STRING, opt), `card_id` (STRING, opt), `pattern_id` (STRING, opt) | `retrieve_similar_cases(customer_id, card_id, pattern_id)` | Historical closed cases, outcomes (`confirmed_fraud` vs `cleared`), analyst notes, actions taken |
| `calculate_case_exposure` | Total fraudulent USD exposure & approval route | `target_case_id` (STRING) | `calculate_case_exposure(target_case_id)` | Total USD exposure, fraudulent transaction count, transaction list, required approval route (`auto`, `L1`, `L2`) |

---

## 2. Detailed Tool Specifications

### Tool 1: `investigate_transaction`

#### Description
Retrieves a complete 360-degree topological profile of a transaction from the TigerGraph fraud graph. Gathers the executing payment card, account holder customer ID, connected hardware/device fingerprint, email domains, billing location, and any prior historical fraud cases attached to the transaction.

#### Input Schema
```json
{
  "type": "object",
  "properties": {
    "txn_id": {
      "type": "string",
      "description": "The unique identifier of the transaction to investigate (e.g. '3514030').",
      "pattern": "^[0-9]{5,10}$"
    }
  },
  "required": ["txn_id"]
}
```
- **Validation Rules:** `txn_id` must be non-empty, numeric string, between 5 and 10 digits.

#### TigerGraph Query Invoked
`investigate_transaction(txn_id=...)`

#### Returned Evidence Structure
```json
{
  "investigation": {
    "target": "3514030",
    "target_type": "Transaction"
  },
  "evidence": [
    {
      "type": "TRANSACTION_RECORD",
      "entity": "3514030",
      "relationship": "TARGET",
      "attributes": {
        "ts": "2016-11-12 00:46:24",
        "amount": 117.0,
        "channel": "in_person",
        "product_cd": "W",
        "risk_score": 0.61,
        "is_flagged": true
      }
    },
    {
      "type": "CARD_INSTRUMENT",
      "entity": "C12382-K1",
      "relationship": "PERFORMED_BY",
      "attributes": {
        "customer_id": "C12382",
        "network": "visa",
        "card_type": "debit"
      }
    },
    {
      "type": "BILLING_REGION",
      "entity": "R_315_87",
      "relationship": "BILLED_IN",
      "attributes": {
        "is_domestic": true
      }
    }
  ],
  "relationships": [
    {"source": "3514030", "edge": "PERFORMED_BY", "target": "C12382-K1"},
    {"source": "C12382-K1", "edge": "OWNED_BY", "target": "C12382"},
    {"source": "3514030", "edge": "BILLED_IN", "target": "R_315_87"}
  ],
  "risk_signals": [
    {"signal": "MODEL_SCORE_ELEVATED", "value": 0.61, "level": "MEDIUM"}
  ],
  "metadata": {
    "query": "investigate_transaction",
    "execution_time_ms": 12
  }
}
```

#### Error Behavior
- If `txn_id` does not exist: Returns structured error `ENTITY_NOT_FOUND`.
- If `txn_id` is empty or invalid format: Returns `INVALID_PARAMETER`.

---

### Tool 2: `trace_connected_entities`

#### Description
Executes multi-hop traversal to discover co-owned cards and syndicate rings sharing identical physical devices, emulators, or proxy configurations across disparate customers. Enforces Rule R6 (*Shared Origin*) and protects portfolio cards under Rule R10.

#### Input Schema
```json
{
  "type": "object",
  "properties": {
    "target_card_id": {
      "type": "string",
      "description": "The card ID to investigate (e.g. 'C08623-K2').",
      "pattern": "^C[0-9]{5}-K[1-9]$"
    },
    "max_hops": {
      "type": "integer",
      "description": "Maximum traversal depth (default: 2, min: 1, max: 3).",
      "default": 2,
      "minimum": 1,
      "maximum": 3
    }
  },
  "required": ["target_card_id"]
}
```

#### TigerGraph Query Invoked
`trace_connected_entities(target_card_id=..., max_hops=...)`

#### Returned Evidence Structure
```json
{
  "investigation": {
    "target": "C08623-K2",
    "target_type": "Card"
  },
  "evidence": [
    {
      "type": "CONNECTED_CARD",
      "entity": "C11923-K2",
      "relationship": "SHARED_DEVICE_SYNDICATE",
      "attributes": {"hop_distance": 2}
    },
    {
      "type": "SHARED_DEVICE",
      "entity": "DEV_a1b2c3d4e5f6",
      "relationship": "USED_DEVICE",
      "attributes": {"device_info": "SAMSUNG SM-G935F"}
    }
  ],
  "relationships": [
    {"source": "C08623-K2", "edge": "USED_DEVICE", "target": "DEV_a1b2c3d4e5f6"},
    {"source": "DEV_a1b2c3d4e5f6", "edge": "USED_IN_TXN", "target": "C11923-K2"}
  ],
  "risk_signals": [
    {"signal": "CROSS_ACCOUNT_DEVICE_SHARING", "severity": "HIGH", "shared_card_count": 2}
  ],
  "metadata": {
    "query": "trace_connected_entities",
    "total_connected_cards": 2,
    "total_shared_devices": 1
  }
}
```

---

### Tool 3: `detect_card_testing`

#### Description
Traverses temporal transaction sequences via `NEXT_TRANSACTION` to detect rapid micro-authorization bursts ($< $5.00) followed by larger cash-out charges. Enforces Rule R5.

#### Input Schema
```json
{
  "type": "object",
  "properties": {
    "target_card_id": {
      "type": "string",
      "description": "The card ID to test (e.g. 'C02923-K1').",
      "pattern": "^C[0-9]{5}-K[1-9]$"
    },
    "window_minutes": {
      "type": "integer",
      "description": "Time window in minutes (default: 60, min: 10, max: 1440).",
      "default": 60,
      "minimum": 10,
      "maximum": 1440
    },
    "micro_threshold": {
      "type": "number",
      "description": "Threshold amount in USD for micro-authorization (default: 5.0).",
      "default": 5.0,
      "minimum": 0.5,
      "maximum": 50.0
    },
    "min_micro_attempts": {
      "type": "integer",
      "description": "Minimum micro-charges to trigger pattern (default: 3).",
      "default": 3,
      "minimum": 1,
      "maximum": 10
    }
  },
  "required": ["target_card_id"]
}
```

#### TigerGraph Query Invoked
`detect_card_testing(target_card_id=..., window_minutes=..., micro_threshold=..., min_micro_attempts=...)`

#### Returned Evidence Structure
```json
{
  "investigation": {
    "target": "C02923-K1",
    "target_type": "Card"
  },
  "evidence": [
    {
      "type": "CARD_TESTING_EVALUATION",
      "entity": "C02923-K1",
      "relationship": "SEQUENCE_ANALYSIS",
      "attributes": {
        "is_detected": true,
        "micro_charge_count": 4,
        "subsequent_large_charge": 284.50
      }
    }
  ],
  "risk_signals": [
    {"signal": "CARD_TESTING_SEQUENCE_CONFIRMED", "severity": "CRITICAL", "policy_rule": "R5"}
  ],
  "metadata": {"query": "detect_card_testing"}
}
```

---

### Tool 4: `analyze_region_anomalies`

#### Description
Compares recent transactions against the cardholder's historical modal billing region to detect out-of-region use vs sustained travel. Enforces Rule R4 and Pattern 4.

#### Input Schema
```json
{
  "type": "object",
  "properties": {
    "target_card_id": {
      "type": "string",
      "description": "The card ID to evaluate.",
      "pattern": "^C[0-9]{5}-K[1-9]$"
    }
  },
  "required": ["target_card_id"]
}
```

#### TigerGraph Query Invoked
`analyze_region_anomalies(target_card_id=...)`

---

### Tool 5: `retrieve_similar_cases`

#### Description
Retrieves historical closed investigations (`closed_cases_history.csv`) matching the customer, card, or candidate fraud typology. Supplies previous analyst notes, verdicts, and actions taken to ground GraphRAG and case memory.

#### Input Schema
```json
{
  "type": "object",
  "properties": {
    "customer_id": {
      "type": "string",
      "description": "Optional customer ID to search (e.g. 'C05876')."
    },
    "card_id": {
      "type": "string",
      "description": "Optional card ID to search (e.g. 'C05876-K2')."
    },
    "pattern_id": {
      "type": "string",
      "description": "Optional pattern typology code to search (e.g. 'out_of_region_use')."
    }
  }
}
```
- **Validation Rules:** At least one of `customer_id`, `card_id`, or `pattern_id` must be provided.

---

### Tool 6: `calculate_case_exposure`

#### Description
Sums the dollar amount of all confirmed fraudulent transactions associated with a case to establish total exposure under Section 4 and determine `auto`, `L1` ($\le \$2,500$), or `L2` ($> \$2,500$) approval routing.

#### Input Schema
```json
{
  "type": "object",
  "properties": {
    "target_case_id": {
      "type": "string",
      "description": "The case ID to evaluate (e.g. 'HHG-001' or 'CC-0001')."
    }
  },
  "required": ["target_case_id"]
}
```

#### TigerGraph Query Invoked
`calculate_case_exposure(target_case_id=...)`

---

## 3. Strict Security & Safety Guarantees

1. **No Arbitrary Querying:** No `run_arbitrary_gsql` or ad-hoc query execution tool is exposed.
2. **Deterministic Schemas:** Every tool maps to exactly one verified GSQL query.
3. **Bounded Numeric Inputs:** All integers and floats are bounded with strict minimum and maximum thresholds.
4. **Input Sanitization:** All string identifiers are validated against strict regex patterns to prevent injection.
5. **No Secret Leakage:** Error responses contain sanitized error codes and messages with zero credential exposure.
