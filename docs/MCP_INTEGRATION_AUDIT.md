# HHGOA TigerGraph MCP Integration Audit Report
**Phase 3 Technical Audit & Architecture Bridge**

---

## 1. Existing TigerGraph Environment

- **Current Environment:** Python 3.11.9 on Windows x64.
- **TigerGraph Python SDK:** `pyTigerGraph` v2.0.4 installed.
- **TigerGraph MCP Server Package:** `tigergraph-mcp` v1.0.3 installed (based on Model Context Protocol `mcp` SDK v2.2.0).
- **Target Graph Engine:** TigerGraph Savanna Cloud (`https://savanna.tgcloud.io`) or TigerGraph Community Edition / Docker.
- **Current Connectivity State:** Local cluster inactive (ports 9000 and 14240 unmapped). Ingest and live query execution remain blocked pending remote workspace URL or container initialization.

---

## 2. Graph Name & Schema Anchor

- **Target Graph Name:** `HHGOA_Fraud_Graph`
- **Vertex Types (9):** `Customer`, `Card`, `Transaction`, `DeviceProfile`, `EmailDomain`, `BillingRegion`, `FraudCase`, `FraudPattern`, `PolicyRule`.
- **Edge Types (13):** `OWNS`, `PERFORMS`, `NEXT_TRANSACTION`, `USED_DEVICE`, `PURCHASER_EMAIL`, `RECIPIENT_EMAIL`, `BILLED_IN`, `INVESTIGATES_TXN`, `TARGETS_CARD`, `CONNECTS_TO_CARD`, `INVESTIGATES_CUSTOMER`, `EXHIBITS_PATTERN`, `GOVERNED_BY` (all equipped with bidirectional reverse edges).

---

## 3. Existing Investigation Queries

The Phase 2 GSQL library contains 6 operational investigation queries and 1 system validation query located in `scripts/tigergraph/queries/`:

1. `investigate_transaction(STRING txn_id)`
2. `trace_connected_entities(STRING target_card_id, INT max_hops = 2)`
3. `detect_card_testing(STRING target_card_id, INT window_minutes = 60, FLOAT micro_threshold = 5.0, INT min_micro_attempts = 3)`
4. `analyze_region_anomalies(STRING target_card_id)`
5. `retrieve_similar_cases(STRING customer_id, STRING card_id, STRING pattern_id)`
6. `calculate_case_exposure(STRING target_case_id)`
7. `validate_graph_metrics()`

---

## 4. Query Inputs & Outputs Audit

| Query | Input Parameters | Output Structure | Investigation Output |
|---|---|---|---|
| `investigate_transaction` | `txn_id` (STRING) | `transaction` tuple, `card_and_customer` tuple, `device_profile` tuple, `purchaser_emails`, `recipient_emails`, `billing_regions`, `associated_cases` | 360° transaction context for alert triage |
| `trace_connected_entities` | `target_card_id` (STRING), `max_hops` (INT) | `connected_entities` list (entity_type, entity_id, connection_path, hop_distance), `total_connected_cards`, `total_shared_devices` | Shared device syndicate ring discovery (Rule R6) |
| `detect_card_testing` | `target_card_id` (STRING), `window_minutes` (INT), `micro_threshold` (FLOAT), `min_micro_attempts` (INT) | `card_id`, `is_card_testing_detected` (BOOL), `micro_authorization_count`, `subsequent_large_charge`, `sequence` list | Card testing velocity sequence detection (Pattern 1, Rule R5) |
| `analyze_region_anomalies` | `target_card_id` (STRING) | `card_id`, `total_transactions`, `region_distribution` map, `international_transaction_count` | Geographic card travel vs out-of-region anomaly (Pattern 4) |
| `retrieve_similar_cases` | `customer_id` (STRING), `card_id` (STRING), `pattern_id` (STRING) | `similar_cases` list (case_id, status, outcome, pattern, exposure_usd, report_filed, actions_taken, analyst_notes, match_reason) | Case memory precedent retrieval for GraphRAG |
| `calculate_case_exposure` | `target_case_id` (STRING) | `case_id`, `total_exposure_usd`, `fraud_transaction_count`, `transaction_ids`, `required_approval_route` (`auto`, `L1`, `L2`) | Financial exposure aggregation and governance routing |

---

## 5. Suitability for MCP Tool Exposure

All 6 investigation queries are strictly read-only, parameterized graph traversals designed specifically for agent consumption:

- **100% Parameterized:** Queries take deterministic, bounded input keys (`txn_id`, `card_id`, `case_id`).
- **No Arbitrary GSQL:** None of the queries permit dynamic string interpolation or user-supplied DDL/DML.
- **Deterministic Schema:** Output structures map cleanly to standardized agent investigation evidence.
- **Validation Query Excluded:** `validate_graph_metrics()` is an operational DBA/audit query, not an investigation tool, and is excluded from agent-facing MCP tools.

---

## 6. Existing Connection Mechanism

- **Primary Driver:** `pyTigerGraph.TigerGraphConnection`.
- **Environment Variables:** `TIGERGRAPH_HOST`, `TIGERGRAPH_PORT`, `TIGERGRAPH_USERNAME`, `TIGERGRAPH_PASSWORD`, `TIGERGRAPH_GRAPH_NAME`, `TIGERGRAPH_SECRET` and standard `TG_*` aliases (`TG_HOST`, `TG_PORT`, `TG_USERNAME`, `TG_PASSWORD`, `TG_GRAPH`, `TG_SECRET`, `TG_TOKEN`).
- **REST++ Endpoints:** Queries are invoked via `POST /restpp/query/HHGOA_Fraud_Graph/<query_name>`.

---

## 7. Missing MCP Components (To Be Implemented in Phase 3)

1. **MCP Tool Wrapper Layer:** Predefined tool wrappers wrapping each of the 6 GSQL queries.
2. **Input Validation Layer:** Pydantic/dataclass schema validators enforcing type safety, non-empty strings, identifier format, and bounded numeric limits.
3. **Evidence Normalization Pipeline:** Transformer that takes raw TigerGraph JSON responses and normalizes them into structured agent evidence (`target`, `evidence`, `relationships`, `risk_signals`, `metadata`).
4. **Resilient Offline/Mock Test Engine:** Allows testing MCP protocol compliance, tool registration, validation, and normalization even when the remote TigerGraph cluster is temporarily paused or unreachable.
5. **Standard MCP Server Entry Point:** Runnable via stdio or SSE transport using the official Model Context Protocol standard.

---

## 8. Blockers & Remediation

- **Blocker:** Live connection to a running TigerGraph instance is currently BLOCKED because no active host or credentials are provided in `.env`.
- **Remediation:** Phase 3 will implement the complete MCP server, schemas, tool wrappers, normalization, error handling, and automated test suite. A dual-mode connection manager will execute against the live cluster if available, and provide verified local offline responses for automated test assertions, ensuring zero faking of live database deployment while delivering fully functional MCP tools.
