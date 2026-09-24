# Benchmark Plan

## Objective
Evaluate the agent on the 20 benchmark cases from the final two months.

## Per-case output
- Internal investigation record
- Evidence
- Findings
- Decisions
- Actions taken
- Case written to TigerGraph
- SAR when required
- Next-best action before additional evidence
- Approval route before additional evidence
- Updated next-best action after additional evidence
- Approval route after additional evidence

## Evaluation dimensions
### Investigation accuracy
Relevant entities, relationships, transactions, patterns, and risk assessment.

### Next-best action
Evidence support, uncertainty handling, evidence requests, updated recommendation, approval route.

### Explainability
Evidence, remaining uncertainty, and action rationale.

### Agentic engineering
Tool use, orchestration, memory, controls, permissions.

## Reproducibility
Record case ID, trigger, tool calls, evidence, state transitions, evidence requests, recommendations, approvals, actions, and final case record.

## Important
The challenge specification states that the transaction data has no `Is Fraud` flag. Do not build the solution around a nonexistent transaction-level fraud label.
