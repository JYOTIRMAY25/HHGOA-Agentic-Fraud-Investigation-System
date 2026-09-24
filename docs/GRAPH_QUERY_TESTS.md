# HHGOA Graph Investigation Query Test Specifications & Evidence Catalogue
**Authoritative GSQL Query Test Suite for Autonomous Fraud Agent**

---

## 1. Overview

This document specifies the test cases, required input parameters, returned output structures, investigation utility, and graph relationship traversals for all GSQL queries implemented in `scripts/tigergraph/queries/`.

Every query is designed to deliver deterministic, structured evidence to the LLM agent during investigation, replacing blind LLM guessing with fast graph traversal.

---

## 2. Query Specifications & Test Cases

### Query 1: `investigate_transaction`

#### Purpose
Provides a comprehensive 360-degree topological profile for any flagged transaction. Gathers the executing payment card, account holder customer ID, connected hardware/device fingerprint, email domains, billing location, and any prior historical fraud cases attached to the transaction.

#### Input
- `txn_id` (STRING): Unique identifier of the transaction (e.g. `"3514030"` from case `HHG-001`).

#### Output Structure
```json
{
  "transaction": [
    {
      "transaction_id": "3514030",
      "ts": "2016-11-12 00:46:24",
      "amount": 117.0,
      "channel": "in_person",
      "product_cd": "W",
      "risk_score": 0.61,
      "is_flagged": true
    }
  ],
  "card_and_customer": [
    {
      "card_id": "C12382-K1",
      "customer_id": "C12382",
      "network": "visa",
      "card_type": "debit"
    }
  ],
  "device_profile": [],
  "purchaser_emails": ["anonymous.com"],
  "recipient_emails": [],
  "billing_regions": ["R_315_87"],
  "associated_cases": ["HHG-001"]
}
```

#### Example Investigation
- **Request:** `RUN QUERY investigate_transaction("3514030")`
- **Result:** Successfully returns transaction metadata showing an in-person charge ($117.00) on card `C12382-K1` owned by customer `C12382`, billed in domestic region `R_315_87`. In-person channel correctly indicates absence of device profile.
- **Evidence Produced:** Confirms channel, cardholder identity, geographic billing region, and baseline risk score.

#### Graph Relationships Used
- **Vertices:** `Transaction`, `Card`, `Customer`, `DeviceProfile`, `EmailDomain`, `BillingRegion`, `FraudCase`
- **Edges:** `PERFORMED_BY`, `OWNED_BY`, `USED_DEVICE`, `PURCHASER_EMAIL`, `RECIPIENT_EMAIL`, `BILLED_IN`, `INVOLVED_IN_CASE`

---

### Query 2: `trace_connected_entities`

#### Purpose
Executes multi-hop traversal to discover co-owned cards and syndicate rings sharing identical physical devices, emulators, or proxy configurations across disparate customers. Enforces Rule R6 (*Shared Origin*) and protects portfolio cards under Rule R10.

#### Input
- `target_card_id` (STRING): The primary card under investigation (e.g. `"C08623-K2"`).
- `max_hops` (INT): Traversal depth (Default: `2`).

#### Output Structure
```json
{
  "connected_entities": [
    {
      "entity_type": "Card",
      "entity_id": "C08623-K1",
      "connection_path": "SAME_CUSTOMER",
      "hop_distance": 1
    },
    {
      "entity_type": "DeviceProfile",
      "entity_id": "DEV_a1b2c3d4e5f6",
      "connection_path": "USED_DEVICE",
      "hop_distance": 1
    },
    {
      "entity_type": "Card",
      "entity_id": "C11923-K2",
      "connection_path": "SHARED_DEVICE_SYNDICATE",
      "hop_distance": 2
    }
  ],
  "total_connected_cards": 2,
  "total_shared_devices": 1
}
```

#### Example Investigation
- **Request:** `RUN QUERY trace_connected_entities("C08623-K2", 2)`
- **Result:** Reveals a shared device fingerprint linking `C08623-K2` to card `C11923-K2` of an unrelated customer, proving coordinated syndicate abuse.
- **Evidence Produced:** Multi-card syndicate link mandating Rule R6 escalation (`CREATE_CASE`, `FILE_REPORT`, `MONITOR_CONNECTED_CARDS`).

#### Graph Relationships Used
- **Vertices:** `Card`, `Customer`, `Transaction`, `DeviceProfile`
- **Edges:** `OWNED_BY`, `OWNS`, `PERFORMS`, `USED_DEVICE`, `USED_IN_TXN`, `PERFORMED_BY`

---

### Query 3: `detect_card_testing`

#### Purpose
Traverses temporal transaction sequences to identify the topological signature of Card Testing (Pattern 1): three or more rapid low-value online authorizations ($< $5.00) followed by a larger cash-out attempt. Enforces Rule R5.

#### Input
- `target_card_id` (STRING): Payment card ID (e.g. `"C02923-K1"`).
- `window_minutes` (INT): Velocity window in minutes (Default: `60`).
- `micro_threshold` (FLOAT): Maximum dollar amount considered a micro-charge (Default: `5.0`).
- `min_micro_attempts` (INT): Minimum micro-charges required to confirm pattern (Default: `3`).

#### Output Structure
```json
{
  "card_id": "C02923-K1",
  "is_card_testing_detected": true,
  "micro_authorization_count": 4,
  "subsequent_large_charge": 284.50,
  "sequence": [
    {"transaction_id": "3100101", "ts": "2016-08-14 10:12:01", "amount": 1.50, "channel": "online", "time_delta_sec": 0},
    {"transaction_id": "3100102", "ts": "2016-08-14 10:14:15", "amount": 2.00, "channel": "online", "time_delta_sec": 134},
    {"transaction_id": "3100103", "ts": "2016-08-14 10:16:40", "amount": 1.25, "channel": "online", "time_delta_sec": 145},
    {"transaction_id": "3100104", "ts": "2016-08-14 10:25:10", "amount": 284.50, "channel": "online", "time_delta_sec": 510}
  ]
}
```

#### Example Investigation
- **Request:** `RUN QUERY detect_card_testing("C02923-K1", 60, 5.0, 3)`
- **Result:** Confirms 3 micro-charges under $2.00 followed by a $284.50 charge within 15 minutes.
- **Evidence Produced:** Clear Card Testing sequence; mandates action `DECLINE_TRANSACTION` and `STEP_UP_AUTH` under Rule R5.

#### Graph Relationships Used
- **Vertices:** `Card`, `Transaction`
- **Edges:** `PERFORMS`, `NEXT_TRANSACTION`

---

### Query 4: `analyze_region_anomalies`

#### Purpose
Analyzes geographic transaction dispersion by comparing recent transactions against the cardholder's historical modal billing region. Distinguishes legitimate continuous travel from impossible simultaneous multi-region card cloning.

#### Input
- `target_card_id` (STRING): Payment card ID (e.g. `"C07297-K1"`).

#### Output Structure
```json
{
  "card_id": "C07297-K1",
  "total_transactions": 28,
  "region_distribution": {
    "R_315_87": 26,
    "R_441_87": 2
  },
  "international_transaction_count": 0
}
```

#### Example Investigation
- **Request:** `RUN QUERY analyze_region_anomalies("C07297-K1")`
- **Result:** Demonstrates 93% of transactions occur in domestic region `R_315_87`, while 2 sudden charges appeared in region `R_441_87`.
- **Evidence Produced:** Isolates regional shift; provides quantitative basis to verify customer travel under Rules R2 and R3.

#### Graph Relationships Used
- **Vertices:** `Card`, `Transaction`, `BillingRegion`
- **Edges:** `PERFORMS`, `BILLED_IN`

---

### Query 5: `retrieve_similar_cases`

#### Purpose
Retrieves historical closed investigations (`closed_cases_history.csv`) matching the customer, card, or candidate fraud typology. Supplies previous analyst notes, verdicts, and actions taken to ground GraphRAG and case memory.

#### Input
- `customer_id` (STRING): Customer ID (e.g. `"C05876"`).
- `card_id` (STRING): Card ID (e.g. `"C05876-K2"`).
- `pattern_id` (STRING): Typology code (e.g. `"out_of_region_use"`).

#### Output Structure
```json
{
  "similar_cases": [
    {
      "case_id": "CC-0003",
      "status": "CLOSED",
      "outcome": "cleared",
      "pattern": "none",
      "exposure_usd": 442.92,
      "report_filed": false,
      "actions_taken": "CLOSE_NO_FRAUD",
      "analyst_notes": "Case CC-0003: model scored a $442.92 transaction at 0.91. Cardholder confirmed travel to the billing region in question. Alert cleared.",
      "match_reason": "SAME_CUSTOMER_PRECEDENT"
    }
  ],
  "precedent_count": 1
}
```

#### Example Investigation
- **Request:** `RUN QUERY retrieve_similar_cases("C05876", "C05876-K2", "out_of_region_use")`
- **Result:** Retrieves Case `CC-0003` showing customer `C05876` previously traveled to an unusual billing region, which was cleared as legitimate.
- **Evidence Produced:** High-value precedent cautioning the agent against an immediate block; strongly supports `VERIFY_WITH_CUSTOMER` under Rule R1.

#### Graph Relationships Used
- **Vertices:** `Customer`, `Card`, `FraudPattern`, `FraudCase`
- **Edges:** `CUSTOMER_CASES`, `HAS_CASES`, `CASES_WITH_PATTERN`

---

### Query 6: `calculate_case_exposure`

#### Purpose
Computes the total confirmed fraudulent exposure in USD across all transactions linked to a case. Automatically outputs the required approval routing level (`auto`, `L1`, or `L2`) based on policy monetary thresholds.

#### Input
- `target_case_id` (STRING): Case identifier (e.g. `"CC-0001"`).

#### Output Structure
```json
{
  "case_id": "CC-0001",
  "total_exposure_usd": 155.43,
  "fraud_transaction_count": 1,
  "transaction_ids": ["3000120"],
  "required_approval_route": "L1"
}
```

#### Example Investigation
- **Request:** `RUN QUERY calculate_case_exposure("CC-0001")`
- **Result:** Computes exposure of $155.43. Since exposure is $\le \$2,500$, routes to `L1` (team lead approval) rather than `L2`.
- **Evidence Produced:** Deterministic compliance calculation determining approval authority for card blocks and case closure.

#### Graph Relationships Used
- **Vertices:** `FraudCase`, `Transaction`
- **Edges:** `INVESTIGATES_TXN`

---

### Query 7: `validate_graph_metrics`

#### Purpose
Performs an exhaustive census of all vertices and edges in the graph, confirming parity with the authoritative dataset audit.

#### Input
- None.

#### Output Structure
```json
{
  "customer_count": 1892,
  "card_count": 1913,
  "transaction_count": 590742,
  "device_profile_count": 1786,
  "email_domain_count": 60,
  "billing_region_count": 332,
  "fraud_case_count": 5585,
  "fraud_pattern_count": 7,
  "policy_rule_count": 10
}
```

#### Graph Relationships Used
- **Vertices:** All 9 vertex types across `HHGOA_Fraud_Graph`.
