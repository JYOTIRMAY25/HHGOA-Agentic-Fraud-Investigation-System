# Agent Workflow

## Investigation loop

```text
Trigger
 ↓
Open/Create Case
 ↓
Select tools
 ↓
Query TigerGraph
 ↓
Retrieve GraphRAG context
 ↓
Synthesize evidence
 ↓
Assess risk + uncertainty
 ↓
Enough evidence?
 ├─ No → identify missing evidence → request controlled evidence
 │       → receive → reassess
 └─ Yes → propose next-best action
          → policy/permission check
          → approval if required
          → execute/simulate
          → explain
          → update memory
```

## Tool categories
### Graph
- Entity lookup
- Connected account discovery
- Shared-device analysis
- Identity relationships
- Transaction relationships
- Prior case retrieval
- Fraud-pattern queries

### Retrieval
- Policy
- Procedures
- Typologies
- Regulatory references
- Similar cases

### Evidence
- Transaction validation
- Step-up authentication
- Analyst/approved-party information

### Case
- Create case
- Add evidence
- Update risk/status
- Record decisions/actions
- Close case

### Memory
- Store outcome
- Retrieve similar cases
- Identify recurring entities/patterns

## Guardrails
- No fabricated evidence.
- No unsupported conclusions.
- No uncontrolled action execution.
- Recommendations must reference recorded evidence.
- Actions must pass policy/permission checks.
- Required approvals must be enforced.
