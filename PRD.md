# TigerGraph Agentic Fraud Investigation HHGOA — PRD

## Objective
Build an AI agent powered by TigerGraph that investigates fraud from an initial trigger, gathers evidence, assesses risk and uncertainty, requests additional evidence when needed, recommends or executes policy-approved next-best actions, explains the decision, and stores the investigation outcome as case memory.

## Required capabilities
- Trigger from fraud signal/risk score, customer report, or analyst request.
- Investigate transactions, entities, relationships, behavior, and prior cases.
- Gather evidence from knowledge graphs, transaction history, device/identity signals, account behavior, prior cases, and complementary external sources.
- Identify fraud patterns and likely fraud type.
- Assess risk and uncertainty.
- Create and progress fraud cases.
- Retrieve and use prior case memory.
- Request controlled additional evidence.
- Recommend or take next-best actions.
- Enforce permissions and approval routes.
- Stop when enough evidence exists for a defensible action.
- Explain evidence, requested evidence, uncertainty, and action rationale.

## Mandatory technology
- TigerGraph Savanna or Community Edition
- GSQL and TigerGraph graph algorithms
- TigerGraph MCP
- GraphRAG
- User interface

## Dataset
HHGOA_IEEE, based on IEEE-CIS Fraud Detection data from Vesta Corporation. The challenge specification states approximately 590,000 transactions, approximately 13,500 customers, device/connection records, bank fraud-model risk scores, no `Is Fraud` flag, closed investigations from the first four months, policy/typology/regulatory references, and 20 benchmark cases from the final two months.

**Read the dataset README first.** Final schema, field mapping, answer format, and benchmark implementation must follow the dataset README.

## Required benchmark output
For every benchmark case:
- Internal investigation record
- Evidence
- Findings
- Decisions
- Actions
- Case written to graph
- SAR when required
- Next-best action and approval route before additional evidence
- Next-best action and approval route after additional evidence

## Success
Demonstrate the complete trigger → investigate → evidence → uncertainty → additional evidence → action → explanation → memory loop.
