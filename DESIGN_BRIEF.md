# Design Brief

## Goal
Create an analyst-focused investigation workspace that makes the complete investigation traceable rather than showing only a final AI answer.

## Priority information
1. Case status
2. Risk and uncertainty
3. Graph relationships
4. Evidence timeline
5. Agent actions
6. Additional evidence requests
7. Next-best action
8. Approval route
9. Explanation
10. Case memory

## Suggested layout
### Header
Case ID, trigger, status, risk score, confidence.

### Graph Workspace
Customer, account, transaction, device, identity, and other relevant entities.

### Evidence Timeline
Timestamp, source, finding, relevance.

### Agent Panel
Evidence considered, uncertainty, missing evidence, investigation state, decision summary.

### Action Panel
Recommended action, reason, policy/approval requirement, status, action history.

## UX principle
Show concise, auditable evidence summaries and decision reasons. Do not expose private hidden chain-of-thought.
