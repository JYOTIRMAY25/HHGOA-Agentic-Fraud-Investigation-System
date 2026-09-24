# MCP Live Validation

**Project:** HHGOA TigerGraph Agentic Fraud Investigation
**Graph:** `HHGOA_Fraud_Graph`
**TigerGraph:** Savanna 4.2.5
**Validation timestamp:** 2026-09-21T22:36:07+05:30
**Status:** BLOCKED — the Savanna workspace still returns the workspace-start error

## Environment

| Variable | Status | Notes |
|---|---|---|
| `TG_HOST` | PRESENT | Savanna endpoint configured |
| `TG_GRAPHNAME` | PRESENT | Resolves to `HHGOA_Fraud_Graph`; legacy graph aliases are also present |
| `TG_TGCLOUD` | PRESENT | `true` |
| `TG_SECRET` | PRESENT | Value intentionally omitted from this report |
| `TG_MOCK_MODE` | PRESENT | `false` for live validation |
| REST port | PRESENT | `443` |

The existing MCP path was used:

`mcp/tools/investigation.py` -> `mcp/connection.py` -> `AsyncTigerGraphConnection` -> Savanna

No alternate connection architecture was created.

## Connection

**BLOCKED**

The configured Savanna endpoint is reachable at the HTTP proxy layer, but the existing async connection's `echo()` request returned HTTP 500. The safe response body was:

> Failed to start workspace — Auto start is not enabled for this workspace

This occurs before graph-specific authentication or query execution can be verified.

## Authentication

**BLOCKED**

Authentication could not be confirmed because the workspace did not start. No credential values were printed or stored in this report.

## Graph

**BLOCKED — existence not determined**

`HHGOA_Fraud_Graph` could not be queried while the workspace was stopped. This is not reported as `GRAPH_NOT_FOUND`; the graph existence check was not reachable.

## Schema

**BLOCKED — live schema not retrieved**

The two local schema sources were checked without modifying the live workspace:

| Local schema source | Vertex types | Edge types |
|---|---:|---:|
| `scripts/tigergraph/schema.gsql` | 9 | 13 |
| `tigergraph/schema/schema.gsql` | 9 | 13 |

The expected design is 9 vertex types and 13 edge types. A live schema comparison was not possible.

## Data

**BLOCKED — live data not verified**

No live vertex or edge counts were available. The processed staging directory is present with 9 vertex CSVs and 13 edge CSVs, but those local files do not prove that data exists in Savanna.

Current staged vertex counts used by the preload validation are:

| Vertex | Staged rows |
|---|---:|
| Customer | 13,553 |
| Card | 13,574 |
| Transaction | 590,742 |
| DeviceProfile | 9,777 |
| EmailDomain | 60 |
| BillingRegion | 437 |
| FraudCase | 5,585 |
| FraudPattern | 7 |
| PolicyRule | 10 |

These are local staging counts only. The raw dataset audit counts and graph-specific staged counts represent different modeling levels; neither was treated as a live TigerGraph result.

## GSQL Queries

**BLOCKED — installation not verified**

The seven local query files are present:

- `investigate_transaction`
- `trace_connected_entities`
- `detect_card_testing`
- `analyze_region_anomalies`
- `retrieve_similar_cases`
- `calculate_case_exposure`
- `validate_graph_metrics`

No query installation or execution status could be retrieved from the stopped workspace. No schema, loading job, or query was installed or modified during this validation.

## MCP Tools

| Tool | Mock | Live | Result |
|---|---|---|---|
| `investigate_transaction` | PASS | BLOCKED | Live path stopped at workspace HTTP 500 |
| `trace_connected_entities` | PASS | BLOCKED | Live connection could not initialize |
| `detect_card_testing` | PASS | BLOCKED | Live connection could not initialize |
| `analyze_region_anomalies` | PASS | BLOCKED | Live connection could not initialize |
| `retrieve_similar_cases` | PASS | BLOCKED | Live connection could not initialize |
| `calculate_case_exposure` | PASS | BLOCKED | Live connection could not initialize |

Live inputs used for the attempt:

- Transaction: `3514030`
- Connected card: `C08623-K2`
- Card-testing card: `C02923-K1`
- Region-analysis card: `C08623-K2`
- Similar-case subject: customer `C05876`, card `C05876-K2`, pattern `out_of_region_use`
- Exposure case: `CC-0001`

All six tools returned their verified offline fixtures with `TG_MOCK_MODE=true`.

## Failure Handling

- Empty transaction ID: returns `INVALID_PARAMETER` without a live request.
- Invalid card format: returns `INVALID_PARAMETER` without a live request.
- Unknown transaction in mock mode: returns `ENTITY_NOT_FOUND`.
- Unavailable TigerGraph: returns a safe `CONNECTION_FAILURE`; no secret is included.
- Missing graph and empty live result: not separately verifiable while the workspace is stopped.

## Blockers

1. The Savanna workspace is stopped.
2. Savanna auto-start is disabled, so the endpoint returns HTTP 500 instead of starting the workspace.
3. The workspace must be started manually in the Savanna console before authentication, graph/schema/data checks, query installation checks, or live MCP tool execution can proceed.

No credentials were exposed, no graph was created or dropped, no data was loaded, and no schema or query files were changed.
