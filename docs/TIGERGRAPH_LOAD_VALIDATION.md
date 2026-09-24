# HHGOA TigerGraph Load Validation Report
**Phase 2 Database Implementation & Integrity Verification**

---

## 1. Executive Summary & Deployment Status

- **Schema Implementation Status:** COMPLETE (`scripts/tigergraph/schema.gsql`)
- **Loading Pipeline Implementation Status:** COMPLETE (`scripts/tigergraph/loading_jobs.gsql`, `scripts/tigergraph/prepare_graph_data.py`)
- **Investigation Queries Implementation Status:** COMPLETE (`scripts/tigergraph/queries/*.gsql`)
- **Live Database Connection Status:** **BLOCKED (NO TIGERGRAPH INSTANCE ACCESSIBLE)**
  - *Audit Fact:* No TigerGraph instance is running or accessible (port 9000/14240 closed). No `.env` file with credentials existed prior to this deployment attempt. TigerGraph cloud endpoint (savanna.tgcloud.io) is reachable at the network level but no workspace/credentials are configured. Docker is not available in this environment.
  - In strict compliance with task instructions (*"If TigerGraph cannot be accessed from the current environment, DO NOT fake successful deployment... mark deployment as BLOCKED rather than COMPLETE"*), the live ingest execution against an active cluster is held pending a provisioned TigerGraph instance with valid credentials.
  - All staging data, GSQL DDL, loading jobs, validation queries, and pyTigerGraph automated scripts have been generated and validated offline.
  - Deployment attempt date: 2026-09-20
  - Connection test result: `ConnectionError` — HTTPConnectionPool(host='127.0.0.1', port=14240): Max retries exceeded. All ports (9000, 14240) closed. No TigerGraph process detected.

---

## 2. Quantitative Entity & Relationship Validation Matrix

The expected numbers below are derived directly from the empirical Phase 1 audit documented in [`docs/DATASET_AUDIT.md`](file:///d:/task4/docs/DATASET_AUDIT.md) and [`docs/DATA_DICTIONARY.csv`](file:///d:/task4/docs/DATA_DICTIONARY.csv).

| Entity / Relationship | Expected (Audit Ground Truth) | Staged for Ingestion | Loaded in Live TG | Difference | Status |
|---|---:|---:|---:|---:|---|
| **Vertices** | | | | | |
| `Transaction` | 590,742 | 590,742 | BLOCKED | 0 | **BLOCKED — NO TIGERGRAPH INSTANCE** |
| `Customer` | 1,892 | 1,892 | BLOCKED | 0 | **BLOCKED — NO TIGERGRAPH INSTANCE** |
| `Card` | 1,913 | 1,913 | BLOCKED | 0 | **BLOCKED — NO TIGERGRAPH INSTANCE** |
| `DeviceProfile` | 1,786 | 1,786 | BLOCKED | 0 | **BLOCKED — NO TIGERGRAPH INSTANCE** |
| `EmailDomain` | 60 | 60 | BLOCKED | 0 | **BLOCKED — NO TIGERGRAPH INSTANCE** |
| `BillingRegion` | 332 | 332 | BLOCKED | 0 | **BLOCKED — NO TIGERGRAPH INSTANCE** |
| `FraudCase` | 5,585 | 5,585 | BLOCKED | 0 | **BLOCKED — NO TIGERGRAPH INSTANCE** |
| `FraudPattern` | 7 | 7 | BLOCKED | 0 | **BLOCKED — NO TIGERGRAPH INSTANCE** |
| `PolicyRule` | 10 | 10 | BLOCKED | 0 | **BLOCKED — NO TIGERGRAPH INSTANCE** |
| **Edges** | | | | | |
| `PERFORMS` (`Card` -> `Transaction`) | 590,742 | 590,742 | BLOCKED | 0 | **BLOCKED — NO TIGERGRAPH INSTANCE** |
| `USED_DEVICE` (`Transaction` -> `DeviceProfile`) | 144,432 | 144,432 | BLOCKED | 0 | **BLOCKED — NO TIGERGRAPH INSTANCE** |
| `NEXT_TRANSACTION` (`Txn` -> `Txn`) | 588,829 | 588,829 | BLOCKED | 0 | **BLOCKED — NO TIGERGRAPH INSTANCE** |
| `BILLED_IN` (`Transaction` -> `BillingRegion`) | 525,027 | 525,027 | BLOCKED | 0 | **BLOCKED — NO TIGERGRAPH INSTANCE** |
| `PURCHASER_EMAIL` (`Txn` -> `EmailDomain`) | 537,745 | 537,745 | BLOCKED | 0 | **BLOCKED — NO TIGERGRAPH INSTANCE** |
| `RECIPIENT_EMAIL` (`Txn` -> `EmailDomain`) | 137,787 | 137,787 | BLOCKED | 0 | **BLOCKED — NO TIGERGRAPH INSTANCE** |
| `INVESTIGATES_TXN` (`Case` -> `Transaction`) | 14,975 | 14,975 | BLOCKED | 0 | **BLOCKED — NO TIGERGRAPH INSTANCE** |
| `TARGETS_CARD` (`Case` -> `Card`) | 5,585 | 5,585 | BLOCKED | 0 | **BLOCKED — NO TIGERGRAPH INSTANCE** |
| `INVESTIGATES_CUSTOMER` (`Case` -> `Customer`) | 5,585 | 5,585 | BLOCKED | 0 | **BLOCKED — NO TIGERGRAPH INSTANCE** |
| `CONNECTS_TO_CARD` (`Case` -> `Card`) | 24 | 24 | BLOCKED | 0 | **BLOCKED — NO TIGERGRAPH INSTANCE** |
| `EXHIBITS_PATTERN` (`Case` -> `FraudPattern`) | 5,565 | 5,565 | BLOCKED | 0 | **BLOCKED — NO TIGERGRAPH INSTANCE** |
| `OWNS` (`Customer` -> `Card`) | 1,913 | 1,913 | BLOCKED | 0 | **BLOCKED — NO TIGERGRAPH INSTANCE** |
| `GOVERNED_BY` (`Case` -> `PolicyRule`) | 5,585 | 5,585 | BLOCKED | 0 | **BLOCKED — NO TIGERGRAPH INSTANCE** |

---

## 3. Referential Integrity Cross-Checks

Before triggering live database loading, referential integrity was verified programmatically across all generated staging files:

1. **Transaction ID Resolution:**
   - Case pack flagged transactions: 20 of 20 (100.0%) match `vertices_transaction.csv`.
   - Closed case transactions: 14,955 of 14,955 (100.0%) match `vertices_transaction.csv`.
   - Dangling/orphan transaction edges: 0.

2. **Customer & Card Mapping:**
   - Case pack customers: 20 of 20 (100.0%) match `vertices_customer.csv`.
   - Closed case customers: 1,892 of 1,892 (100.0%) match `vertices_customer.csv`.
   - Connected cards: All 24 cards resolve to valid customer prefixes in the graph.

3. **Digital Attribution Integrity:**
   - All 144,432 `USED_DEVICE` edges reference valid online transactions and exist in `vertices_device_profile.csv`.
   - In-person transactions (`channel == "in_person"`, 439,670 rows) have 0 device edges, matching the dataset rule.

---

## 4. Execution Plan to Unblock Live Cluster Deployment

To execute live loading against a TigerGraph cluster:

1. **Start TigerGraph or Provision Savanna Cloud Instance:**
   - Free Savanna Workspace: `https://savanna.tgcloud.io`
   - Or local Docker container: `docker run -d -p 9000:9000 -p 14240:14240 tigergraph/tigergraph:latest`

2. **Set Credentials in `.env`:**
   ```bash
   TIGERGRAPH_HOST=https://your-workspace.i.tgcloud.io
   TIGERGRAPH_USERNAME=tigergraph
   TIGERGRAPH_PASSWORD=your_password
   TIGERGRAPH_GRAPH_NAME=HHGOA_Fraud_Graph
   ```

3. **Run Automated Deployment:**
   ```bash
   python scripts/tigergraph/load_data.py
   python scripts/tigergraph/validate_graph.py
   ```

Upon execution, the query `validate_graph_metrics` will populate the "Loaded in Live TG" column above.
