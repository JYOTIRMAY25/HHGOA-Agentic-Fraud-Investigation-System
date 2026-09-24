# User Flow

1. Investigation is triggered.
2. Agent creates or opens a case.
3. Initial risk signal is displayed.
4. Agent identifies relevant entities.
5. Agent queries TigerGraph through MCP.
6. Agent retrieves connected transactions, accounts, devices, identities, and prior cases.
7. GraphRAG retrieves relevant policy, typology, and regulatory context.
8. Agent synthesizes evidence.
9. Agent assesses fraud type, risk, confidence, and uncertainty.
10. Agent determines whether evidence is sufficient.
11. If insufficient, agent requests controlled additional evidence.
12. New evidence is received or simulated.
13. Agent reassesses.
14. Agent recommends next-best action.
15. Permission/approval route is checked.
16. Action is executed or simulated.
17. Decision explanation is recorded.
18. Case is updated.
19. Outcome is stored as memory.

## Main UI areas
- Case list
- Investigation overview
- Fraud graph
- Evidence timeline
- Risk/uncertainty
- Evidence requests
- Recommendation/approval
- Case history/memory
- Final case summary
