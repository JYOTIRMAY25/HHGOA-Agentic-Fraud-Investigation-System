# System Architecture

```text
Trigger
  ↓
Investigation API
  ↓
Agent Orchestrator
  ├── TigerGraph MCP
  ├── GraphRAG
  ├── Case Memory
  ├── Evidence Tools
  └── Policy/Approval Tools
  ↓
Evidence Synthesis
  ↓
Risk + Uncertainty
  ↓
Enough Evidence?
 ├── No → Controlled Evidence Request → New Evidence → Reassess
 └── Yes → Next-Best Action → Approval/Permission → Execute or Simulate
  ↓
Explain Decision
  ↓
Update Case + Memory
```

## Components
### Agent Orchestrator
Runs the investigation state machine and selects tools.

### TigerGraph MCP
Exposes controlled graph capabilities and data to the agent.

### TigerGraph/GSQL
Performs graph traversal, connected-entity analysis, relationship analysis, and fraud-pattern investigation.

### GraphRAG
Retrieves relevant graph evidence and document context such as policies, procedures, typologies, and regulatory references.

### Policy/Permission Layer
Determines whether an action is allowed, requires approval, or cannot be executed.

### Case Manager
Creates and updates cases, evidence, findings, decisions, actions, and outcomes.

### Memory
Retrieves similar cases and stores outcomes for future investigations.

## State Machine
`TRIGGERED → INVESTIGATING → EVIDENCE_GATHERED → ASSESSING → NEED_MORE_EVIDENCE / ACTION_PROPOSED → APPROVAL_REQUIRED / READY → ACTION_RECORDED → EXPLAINED → MEMORY_UPDATED → CLOSED`
