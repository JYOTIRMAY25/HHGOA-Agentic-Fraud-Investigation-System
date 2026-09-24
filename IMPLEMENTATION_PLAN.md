# HHGOA TigerGraph Agentic Fraud Investigation — Implementation Plan & Status

---

## Project Status Overview

| Phase | Milestone | Status | Artifacts / Deliverables |
|---|---|---|---|
| **Phase 1** | Dataset Audit & Data Dictionary | **COMPLETE** | `docs/DATASET_AUDIT.md`, `docs/DATA_DICTIONARY.csv` |
| **Phase 2** | Graph Schema & Architecture Design | **COMPLETE** | `docs/TIGERGRAPH_SCHEMA.md` |
| **Phase 2** | GSQL DDL Implementation | **COMPLETE** | `scripts/tigergraph/schema.gsql`, `tigergraph/schema/schema.gsql` |
| **Phase 2** | Data Staging & Loading Jobs | **COMPLETE** | `scripts/tigergraph/loading_jobs.gsql`, `scripts/tigergraph/prepare_graph_data.py` |
| **Phase 2** | Live TigerGraph Cluster Ingestion | **BLOCKED** | No TigerGraph instance accessible. All .env placeholders. Docker unavailable. (docs/TIGERGRAPH_LOAD_VALIDATION.md) |
| **Phase 2** | GSQL Investigation Queries | **COMPLETE** | `scripts/tigergraph/queries/*.gsql`, `tigergraph/gsql/*.gsql` (7 queries) |
| **Phase 2** | Query Test Suite & Specifications | **COMPLETE** | `docs/GRAPH_QUERY_TESTS.md` |
| **Phase 2** | Operations Manual & Setup Guide | **COMPLETE** | `docs/TIGERGRAPH_SETUP.md`, `.env.example` |
| **Phase 3** | TigerGraph MCP Integration | **VALIDATED (MOCK)** | Custom investigation tools working via `TG_MOCK_MODE=true`. 6 tools tested with offline fixtures. Official tigergraph-mcp has dep issue. |
| **Phase 4** | GraphRAG Knowledge Engine | **TODO** | Vector embeddings, regulatory retrieval |
| **Phase 5** | Autonomous Fraud Investigation Agent | **TODO** | Multi-step reasoning state machine |
| **Phase 6** | Benchmark Evaluation (20 Cases) | **TODO** | 20 case deliverable JSON answers in `cases/` |
| **Phase 7** | Frontend / Demonstration UI | **TODO** | Interactive case review dashboard |

---

## Detailed Task Breakdown

### Phase 1: Dataset Audit & Validation
- [x] Read and cross-examine dataset `README.md`. **[COMPLETE]**
- [x] Audit row counts and data types across `transactions.csv`, `identity.csv`, `closed_cases_history.csv`, and `case_pack.csv`. **[COMPLETE]**
- [x] Execute referential integrity checks (100% resolution of transaction and customer IDs). **[COMPLETE]**
- [x] Document 461-column data dictionary in `docs/DATA_DICTIONARY.csv`. **[COMPLETE]**
- [x] Produce comprehensive report in `docs/DATASET_AUDIT.md`. **[COMPLETE]**

### Phase 2: TigerGraph Database Implementation
- [x] Design graph schema with 9 vertex types and 13 edge types in `docs/TIGERGRAPH_SCHEMA.md`. **[COMPLETE]**
- [x] Implement production GSQL DDL script in `scripts/tigergraph/schema.gsql`. **[COMPLETE]**
- [x] Implement native GSQL loading job definitions in `scripts/tigergraph/loading_jobs.gsql`. **[COMPLETE]**
- [x] Develop high-performance staging pipeline in `scripts/tigergraph/prepare_graph_data.py`. **[COMPLETE]**
- [x] Implement automated Python loader with `pyTigerGraph` in `scripts/tigergraph/load_data.py`. **[COMPLETE]**
- [ ] Connect to active TigerGraph cluster and load 590,742 transactions. **[BLOCKED]** *(No TigerGraph instance accessible — all ports closed, no .env credentials, Docker unavailable — 2026-09-20)*
- [x] Document load validation matrix and expected metrics in `docs/TIGERGRAPH_LOAD_VALIDATION.md`. **[COMPLETE]**
- [x] Implement 6 GSQL investigation queries and validation census query in `scripts/tigergraph/queries/`. **[COMPLETE]**
- [x] Document query inputs, outputs, examples, and graph traversals in `docs/GRAPH_QUERY_TESTS.md`. **[COMPLETE]**
- [x] Document deployment guide and operational procedures in `docs/TIGERGRAPH_SETUP.md`. **[COMPLETE]**
- [x] Provide clean `.env.example` template without secrets. **[COMPLETE]**

### Phase 3: TigerGraph MCP Server Integration
- [x] Install TigerGraph MCP server dependencies. **[COMPLETE]** (tigergraph-mcp v1.0.3, pyTigerGraph v2.0.4 verified)
- [x] Expose GSQL investigation queries as callable agent tools via MCP. **[COMPLETE]** (mcp/tools/investigation.py: 6 execute functions, mcp/connection.py: 7 fixture handlers)
- [x] Validate MCP tool schemas and parameter passing in mock mode. **[COMPLETE]** (All 6 investigation tools tested with `TG_MOCK_MODE=true` using verified offline fixtures from Phase 1 audit)
- [ ] Validate MCP tool schemas and JSON-RPC parameter passing against live TigerGraph. **[BLOCKED]** *(Requires live TigerGraph cluster; mock validation passed)*

### Phase 4: GraphRAG Knowledge Engine
- [ ] Ingest regulatory guidance (FinCEN SAR, FATF, FFIEC) and bank policy into vector store. **[TODO]**
- [ ] Index 5,565 closed case analyst notes for hybrid topological-semantic retrieval. **[TODO]**
- [ ] Build contextual prompt generator combining graph neighborhood and precedent cases. **[TODO]**

### Phase 5: Autonomous Fraud Investigation Agent
- [ ] Implement agent state machine (Trigger -> Investigate -> Assess -> Propose Action -> Policy Check -> Approval Route -> Explain). **[TODO]**
- [ ] Enforce Fraud Policy rules R1 through R10 with deterministic rule execution. **[TODO]**
- [ ] Simulate evidence request interactions (customer verification, step-up auth). **[TODO]**
- [ ] Implement case memory write-back to graph upon investigation closure. **[TODO]**

### Phase 6: Benchmark Execution & Regulatory SAR Reporting
- [ ] Execute agent on all 20 exam cases in `case_pack.csv`. **[TODO]**
- [ ] Generate 20 compliant JSON answers in `cases/<case_id>.json`. **[TODO]**
- [ ] Verify standalone regulatory SAR narratives when `FILE_REPORT` is mandated. **[TODO]**
- [ ] Validate before-and-after evidence recommendations and approval routes (`auto`, `L1`, `L2`). **[TODO]**
