# Engineering Plan

## Phase 0 — Dataset Audit
1. Obtain HHGOA_IEEE.
2. Read README first.
3. Inventory files and columns.
4. Understand case structure and answer format.
5. Understand policy, five known patterns, and regulatory references.
6. Identify the 20 benchmark cases.

## Phase 1 — Data Layer
1. Create repeatable ingestion.
2. Validate rows and columns.
3. Preserve raw data.
4. Normalize only where required.
5. Create benchmark-case loader.

## Phase 2 — TigerGraph
1. Create graph schema.
2. Load entities.
3. Create relationships.
4. Implement GSQL.
5. Validate graph traversal and fraud-pattern queries.

## Phase 3 — MCP
1. Configure TigerGraph MCP.
2. Expose required graph tools.
3. Test tool access.
4. Restrict authorized operations.

## Phase 4 — GraphRAG
1. Index policy/procedure/typology/regulatory documents.
2. Retrieve graph evidence.
3. Retrieve document evidence.
4. Build grounded context.
5. Track sources.

## Phase 5 — Agent
1. Implement investigation state machine.
2. Add tool selection.
3. Add evidence synthesis.
4. Add uncertainty assessment.
5. Add additional-evidence requests.
6. Add next-best-action reasoning.
7. Add policy/approval controller.
8. Add case memory.
9. Add explanations.

## Phase 6 — Benchmark
Run all 20 cases and generate required output files.

## Phase 7 — UI
Case list, investigation view, graph, evidence, uncertainty, recommendation, approval, timeline, memory.

## Phase 8 — Submission
Working agent, GitHub, 20-case outputs, 3–5 minute demo, technical blog, X/LinkedIn post tagging @TigerGraphDB.
