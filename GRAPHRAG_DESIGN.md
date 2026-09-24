# GraphRAG Design

## Objective
Ground the agent with relevant graph evidence and document context instead of passing raw data blindly to the LLM.

## Sources
### Graph
- Relevant transaction
- Connected account
- Device
- Identity
- Prior fraud cases
- Findings
- Actions/outcomes

### Documents
- Fraud policy
- Procedures
- Five known fraud patterns
- Regulatory references
- Dataset documentation

## Retrieval
```text
Case
 ↓
Identify entities + investigation question
 ↓
Graph retrieval + document retrieval
 ↓
Filter/rank relevant evidence
 ↓
Build grounded context
 ↓
LLM reasoning/tool selection/explanation
```

## Context package
```json
{
  "case_id": "...",
  "trigger": "...",
  "risk_signal": "...",
  "graph_evidence": [],
  "document_evidence": [],
  "prior_cases": [],
  "open_questions": [],
  "policy_constraints": [],
  "uncertainty": {}
}
```

## Rules
- Preserve evidence source identifiers.
- Distinguish observed evidence from inferred conclusions.
- Do not fabricate missing information.
- Important recommendations should be traceable to retrieved evidence.
