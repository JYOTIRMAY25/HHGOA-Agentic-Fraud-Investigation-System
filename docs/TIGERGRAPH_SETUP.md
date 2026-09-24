# HHGOA TigerGraph Database Operations Manual
**Complete Deployment, Ingestion, and Query Execution Guide**

---

## 1. System Requirements & Environment Assumptions

- **TigerGraph Version:** TigerGraph 3.9+ or 4.x (Community Edition, Docker, or TigerGraph Savanna Cloud).
- **Python Runtime:** Python 3.11+ with `pyTigerGraph` and `python-dotenv` installed.
- **Operating Systems:** Windows 10/11, Linux (Ubuntu 20.04/22.04 LTS), or macOS.
- **Port Requirements:**
  - `9000`: REST++ API
  - `14240`: TigerGraph GraphStudio UI
  - `443`: SSL/HTTPS when using TigerGraph Cloud / Savanna

---

## 2. Configuration & Environment Setup

### 2.1 Install Dependencies
```bash
pip install pytigergraph python-dotenv pandas numpy
```

### 2.2 Configure `.env`
Copy the template file to `.env`:
```bash
cp .env.example .env
```

Edit `.env` to match your environment:

#### Option A: TigerGraph Savanna Cloud (Recommended)
1. Sign up for a free workspace at [https://savanna.tgcloud.io](https://savanna.tgcloud.io).
2. Configure `.env`:
```ini
TIGERGRAPH_HOST=https://your-workspace-subdomain.i.tgcloud.io
TIGERGRAPH_PORT=443
TIGERGRAPH_USERNAME=tigergraph
TIGERGRAPH_PASSWORD=YourSecurePassword
TIGERGRAPH_GRAPH_NAME=HHGOA_Fraud_Graph
TIGERGRAPH_SECRET=YourGeneratedSecret
```

#### Option B: Local Docker / Community Edition
1. Run TigerGraph container:
```bash
docker run -d --name tigergraph -p 9000:9000 -p 14240:14240 tigergraph/tigergraph:latest
```
2. Configure `.env`:
```ini
TIGERGRAPH_HOST=http://127.0.0.1
TIGERGRAPH_PORT=9000
TIGERGRAPH_USERNAME=tigergraph
TIGERGRAPH_PASSWORD=tigergraph
TIGERGRAPH_GRAPH_NAME=HHGOA_Fraud_Graph
```

### 2.3 Current Deployment Status

**DEPLOYMENT STATUS: BLOCKED**

No live TigerGraph instance is currently accessible. All schema, queries, loading jobs, and scripts are fully implemented and ready for deployment.

**Prerequisites to unblock:**
- Provision a TigerGraph Savanna workspace at https://savanna.tgcloud.io, OR
- Start a local TigerGraph Community Edition Docker container, OR
- Obtain TigerGraph connection credentials from the developer

**Required configuration in `.env`:**
- `TIGERGRAPH_HOST`: TigerGraph server URL or IP
- `TIGERGRAPH_PORT`: REST++ port (9000 for local, 443 for Savanna)
- `TIGERGRAPH_USERNAME`: Authentication username
- `TIGERGRAPH_PASSWORD`: Authentication password
- `TIGERGRAPH_GRAPH_NAME`: `HHGOA_Fraud_Graph`

---

## 3. Automated End-to-End Pipeline

### Step 1: Pre-Process and Stage Data
Generates normalized, referentially complete vertex and edge files in `data/processed/`:
```bash
python scripts/tigergraph/prepare_graph_data.py
```

### Step 2: Deploy Schema and Load Data
Connects to TigerGraph, applies GSQL DDL, and triggers loading jobs:
```bash
python scripts/tigergraph/load_data.py
```

### Step 3: Run Graph Validation
Verifies that all loaded vertex and edge counts match `docs/DATASET_AUDIT.md`:
```bash
python scripts/tigergraph/validate_graph.py
```

---

## 4. Manual GSQL CLI Operations

If deploying directly via the `gsql` command-line tool:

### 4.1 Schema Deployment
```bash
gsql scripts/tigergraph/schema.gsql
```

### 4.2 Loading Job Installation & Execution
```bash
gsql -g HHGOA_Fraud_Graph scripts/tigergraph/loading_jobs.gsql
gsql -g HHGOA_Fraud_Graph "RUN LOADING JOB load_hhgoa_processed"
```

### 4.3 Install Investigation Queries
```bash
gsql -g HHGOA_Fraud_Graph scripts/tigergraph/queries/investigate_transaction.gsql
gsql -g HHGOA_Fraud_Graph scripts/tigergraph/queries/trace_connected_entities.gsql
gsql -g HHGOA_Fraud_Graph scripts/tigergraph/queries/detect_card_testing.gsql
gsql -g HHGOA_Fraud_Graph scripts/tigergraph/queries/analyze_region_anomalies.gsql
gsql -g HHGOA_Fraud_Graph scripts/tigergraph/queries/retrieve_similar_cases.gsql
gsql -g HHGOA_Fraud_Graph scripts/tigergraph/queries/calculate_case_exposure.gsql
gsql -g HHGOA_Fraud_Graph scripts/tigergraph/queries/validation_queries.gsql

# Compile and install all queries in graph catalog
gsql -g HHGOA_Fraud_Graph "INSTALL QUERY ALL"
```

---

## 5. Query Execution Examples

Execute queries using the REST++ API or GSQL CLI:

### Example 1: 360-Degree Transaction Profile
```bash
curl -X GET "http://localhost:9000/query/HHGOA_Fraud_Graph/investigate_transaction?txn_id=3514030"
```

### Example 2: Multi-Hop Syndicate Ring Tracing
```bash
curl -X GET "http://localhost:9000/query/HHGOA_Fraud_Graph/trace_connected_entities?target_card_id=C08623-K2&max_hops=2"
```

### Example 3: Card Testing Burst Detection
```bash
curl -X GET "http://localhost:9000/query/HHGOA_Fraud_Graph/detect_card_testing?target_card_id=C02923-K1"
```

### Example 4: Precedent Case Memory Retrieval
```bash
curl -X GET "http://localhost:9000/query/HHGOA_Fraud_Graph/retrieve_similar_cases?customer_id=C05876&card_id=C05876-K2&pattern_id=out_of_region_use"
```

---

## 6. Troubleshooting & Operational FAQs

### 1. Connection Refused on Port 9000 / 14240
- **Cause:** TigerGraph service is not running or ports are not mapped.
- **Fix:** Check service status: `docker ps` or in Savanna check workspace state ("Running"). Note that Savanna instances automatically pause when idle; click "Resume" in the TigerGraph Cloud console.

### 2. Schema Conflicts
- **Fix:** To cleanly drop and re-initialize the schema:
```gsql
DROP GRAPH HHGOA_Fraud_Graph
DROP JOB ALL
```

### 3. Missing Reverse Edges during Query Compilation
- **Fix:** All edges in `schema.gsql` define explicit reverse edges (`WITH REVERSE_EDGE`). Ensure queries reference reverse edge names (e.g. `OWNED_BY`, `USED_IN_TXN`) exactly as declared.

---

## 7. Security Policy
- **No Credentials in Source Control:** `.env` is explicitly ignored in `.gitignore`.
- **Read-Only Investigation Access:** Investigation queries are strictly read-only traversals.
- **Case Memory Updates:** Write actions back to `FraudCase` occur through dedicated transactional endpoints.
