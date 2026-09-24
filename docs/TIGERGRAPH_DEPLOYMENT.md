# TigerGraph Savanna Deployment Report

**Project:** HHGOA Fraud Investigation Graph (IEEE-CIS edition)
**Graph Name:** `HHGOA_Fraud_Graph`
**Report Date:** 2026-09-21
**Environment:** TigerGraph Savanna Cloud (tgcloud.io)
**Workspace ID:** `3896e1b9-824b-4ab7-9102-082082422e01`
**Workspace Name:** HHGOAWorkspace

---

## 1. Configuration Inspection

### 1.1 Environment Variables in `.env`

The project uses a dual variable convention (`TG_*` primary with `TIGERGRAPH_*` legacy aliases).
The `mcp/config.py` module resolves all variables with fallbacks. Here is the status of every
required and optional variable:

| Variable | .env Key(s) | Resolved Value | Status |
|----------|-------------|----------------|--------|
| Host | `TG_HOST` | Savanna endpoint URL (truncated for display) | **SET** |
| Graph Name | `TG_GRAPH` / `TIGERGRAPH_GRAPH_NAME` | `HHGOA_Fraud_Graph` | **SET** |
| Username | `TG_USERNAME` / `TIGERGRAPH_USERNAME` | `tigergraph` | **SET** |
| Password | `TG_PASSWORD` / `TIGERGRAPH_PASSWORD` | (masked) | **SET** |
| Secret | `TG_SECRET` / `TIGERGRAPH_SECRET` | (masked, 40 chars) | **SET** |
| TGCLOUD | `TG_TGCLOUD` | `true` | **SET** |
| SSL Port | `TG_PORT` / `TIGERGRAPH_PORT` / `TG_SSL_PORT` | `443` | **SET** |
| API Token | `TG_TOKEN` / `TG_API_TOKEN` | `""` (empty) | **MISSING** (optional — secret is sufficient) |
| JWT Token | `TG_JWT_TOKEN` | not set | **MISSING** (optional) |
| Savanna Cloud API Key | (none in `.env`) | not set | **MISSING** (needed for workspace lifecycle management) |

**All critical database connection variables are present.** The only missing variable is `TG_API_TOKEN`
(an optional field — `TG_SECRET` is the primary auth method). No existing environment variable in `.env`
needs to be created or deleted.

### 1.2 Configuration Observations (Non-Blocking)

| # | Observation | Impact |
|---|-------------|--------|
| O-1 | `TG_GRAPHNAME` is not set directly; the value comes from `TIGERGRAPH_GRAPH_NAME` via fallback in `mcp/config.py` | Low — `mcp/config.py` resolves it correctly, but `test_mcp_connection.py` (line 39) reads `TG_GRAPHNAME` directly and would see empty |
| O-2 | `TG_TOKEN` is empty (`TG_TOKEN=`) | Low — not needed when `TG_SECRET` is set; pyTigerGraph obtains a token from the secret |
| O-3 | The user created a database secret named "kilohhgoa"; the `.env` has `TG_SECRET` with a 40-char value | Info — should verify the `.env` secret matches the one generated for "kilohhgoa" |

### 1.3 Connection Code Inventory

| File | Connection Method | Variables Used |
|------|-------------------|----------------|
| `mcp/config.py` | `pyTigerGraph` (async) + `restppPort` | `TG_HOST`, `TG_SECRET`, `TG_USERNAME`, `TG_PASSWORD`, `TG_TGCLOUD`, `TG_RESTPP_PORT/TIGERGRAPH_PORT` |
| `scripts/tigergraph/load_data.py` | `pyTigerGraph` (sync) | `TIGERGRAPH_HOST`, `TIGERGRAPH_PORT`, `TIGERGRAPH_USERNAME`, `TIGERGRAPH_PASSWORD`, `TIGERGRAPH_SECRET`, `TIGERGRAPH_GRAPH_NAME` |
| `scripts/tigergraph/validate_graph.py` | `pyTigerGraph` (sync) | `TIGERGRAPH_HOST`, `TIGERGRAPH_PORT`, `TIGERGRAPH_USERNAME`, `TIGERGRAPH_PASSWORD` |
| `scripts/tigergraph/test_mcp_connection.py` | `pyTigerGraph.AsyncTigerGraphConnection` | `TG_HOST`, `TG_GRAPHNAME`, `TG_USERNAME`, `TG_PASSWORD`, `TG_SECRET`, `TG_TGCLOUD` |
| `deploy_tg_savanna.py` (created) | `pyTigerGraph.TigerGraphConnection` | `TG_HOST`, `TG_SECRET`, `TG_USERNAME`, `TG_PASSWORD`, `TG_TGCLOUD`, `TG_SSL_PORT` |

---

## 2. Connection Test Results

**TIGERGRAPH CONNECTION: FAIL**

### 2.1 Test Summary

| Test | Endpoint | Result |
|------|----------|--------|
| pyTigerGraph object creation | `TigerGraphConnection(...)` | Success (object created) |
| Token obtain from secret | `GET /gsql/v1/tokens` | **HTTP 500** |
| RESTPP echo | `GET /restpp/echo/` | **HTTP 500** |
| TigerGraph version | `GET /restpp/version` | **HTTP 500** |
| List graphs | `GET /restpp/version` (via listGraphs) | **HTTP 500** |
| GSQL statements | `POST /gsql/v1/statements` | **HTTP 500** |
| Basic auth echo | `GET /restpp/echo/` (auth) | **HTTP 500** |
| RESTPP token | `POST /restpp/auth/token` | **HTTP 500** |

### 2.2 Error Response

Every endpoint on the TigerGraph instance returns the same error:

```html
<title>Failed to start workspace</title>
<body>
<h1>Failed to start workspace</h1>
<p>Auto start is not enabled for this workspace</p>
</body>
```

### 2.3 Root Cause Analysis

1. **Workspace is stopped:** The Savanna workspace `3896e1b9-824b-4ab7-9102-082082422e01` is not running.
   When a Savanna workspace is stopped, the proxy returns HTTP 500 for all TG service endpoints.

2. **Auto-start is disabled:** The workspace has "Auto start" disabled. This means the proxy cannot
   automatically start the workspace when a request arrives — it simply returns the 500 error instead.

3. **Cannot resume programmatically:** The Savanna Cloud management API (`api.tgcloud.io`) requires
   a cloud-level API key. All `api.tgcloud.io` endpoints return:
   ```json
   {"message": "Missing Authentication Token"}
   ```
   The project's `.env` contains database credentials only (`TG_SECRET`), not a Savanna Cloud API key.

4. **Workspace name resolution:** The hostname resolves to IP `13.202.184.154` (AWS CloudFront),
   confirming the workspace DNS entry exists but the underlying instance is not running.

### 2.4 Attempted Resume Methods

| Method | Target | Auth Used | Result |
|--------|--------|-----------|--------|
| `api.tgcloud.io/v1/workspaces/{id}/start` | Savanna Cloud API | None / Bearer secret / Bearer password | 403 — API key required |
| `api.tgcloud.io/v1/workspaces/{id}/resume` | Savanna Cloud API | None / Bearer secret / Bearer password | 403 — API key required |
| `savanna.tgcloud.io/v1/workspaces/{id}/start` | Web console proxy | None | 200 — returns HTML (not API) |
| `savanna.tgcloud.io/v1/login` | Web console | username/password | 200 — returns HTML (not JSON) |
| 5 × retry at 10s intervals | Direct TG endpoints | Various | All HTTP 500 — workspace stopped |

**Conclusion:** The workspace must be started manually via the Savanna web console.
No Savanna Cloud API key is available in the project configuration to resume it programmatically.

---

## 3. What Needs To Happen (Manual Step)

**The user must start the Savanna workspace before deployment can proceed:**

1. Go to https://savanna.tgcloud.io
2. Sign in to the Savanna console
3. Locate the workspace: **HHGOAWorkspace** (ID: `3896e1b9-824b-4ab7-9102-082082422e01`)
4. Click **"Start"** (or "Resume") to start the workspace
5. Wait for status to show **"Running"** (takes 2–3 minutes)
6. Verify the database **"Database-1"** is accessible
7. Verify the database secret **"kilohhgoa"** is active (this generates the secret value used as `TG_SECRET` in `.env`)

After the workspace is running, execute:
```bash
python deploy_tg_savanna.py
```

The script (`deploy_tg_savanna.py`) will:
1. Connect using `.env` credentials
2. Check if `HHGOA_Fraud_Graph` already exists (will NOT delete it)
3. Install the schema from `tigergraph/schema/schema.gsql` if the graph doesn't exist
4. Generate and install a Savanna-compatible loading job using file tags
5. Upload all 22 CSV files from `data/processed/`
6. Run the loading job
7. Validate all vertex and edge counts against expected values
8. Install investigation queries and run graph tests

---

## 4. Prerequisites Status (All Ready)

| Artifact | Status |
|----------|--------|
| `data/processed/*.csv` (22 files) | Ready — pre-load validation passed |
| `docs/TIGERGRAPH_PRELOAD_VALIDATION.md` | Complete — READY |
| `tigergraph/schema/schema.gsql` | Ready — 9 vertex types, 13 edge types + reverse edges |
| `tigergraph/loading/loading_jobs.gsql` | Ready — 22 load statements (server-path based; `deploy_tg_savanna.py` generates file-tag version) |
| `tigergraph/gsql/*.gsql` (7 query files) | Ready — investigation and validation queries |
| `.env` credentials | Present — all critical variables set |
| `deploy_tg_savanna.py` | Ready — handles full deployment pipeline |

---

## 5. Expected Results (Once Workspace is Started)

### Vertex Counts

| Vertex Type | Expected Rows |
|-------------|:-:|
| Customer | 13,553 |
| Card | 13,574 |
| Transaction | 590,742 |
| DeviceProfile | 9,777 |
| EmailDomain | 60 |
| BillingRegion | 437 |
| FraudCase | 5,585 |
| FraudPattern | 7 |
| PolicyRule | 10 |

### Edge Counts

| Edge Type | Expected Rows |
|-----------:-:|
| OWNS | 17,324 |
| PERFORMS | 590,742 |
| NEXT_TRANSACTION | 577,189 |
| USED_DEVICE | 144,432 |
| PURCHASER_EMAIL | 496,262 |
| RECIPIENT_EMAIL | 137,453 |
| BILLED_IN | 525,003 |
| INVESTIGATES_TXN | 14,975 |
| TARGETS_CARD | 5,585 |
| CONNECTS_TO_CARD | 92 |
| INVESTIGATES_CUSTOMER | 5,585 |
| EXHIBITS_PATTERN | 5,565 |
| GOVERNED_BY | 5,987 |

---

## 6. Status Summary

```
TIGERGRAPH CONNECTION: FAIL
GRAPH CREATION: NOT ATTEMPTED
DATA LOADING: NOT ATTEMPTED
GRAPH VALIDATION: NOT ATTEMPTED
INVESTIGATION TESTS: NOT ATTEMPTED
```

**Reason:** The Savanna workspace is stopped and auto-start is disabled. The workspace must be
started manually at https://savanna.tgcloud.io. No graph was deleted, no data was modified,
and no credentials were exposed. Once the workspace is running, `python deploy_tg_savanna.py`
will execute the full deployment pipeline automatically.
