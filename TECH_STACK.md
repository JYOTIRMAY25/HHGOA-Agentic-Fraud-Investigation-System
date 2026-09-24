# Technical Stack

## Mandatory
| Layer | Technology |
|---|---|
| Graph | TigerGraph Savanna or Community Edition |
| Graph analysis | GSQL + TigerGraph graph algorithms |
| Agent/graph interface | TigerGraph MCP |
| Grounding | GraphRAG |
| Dataset | HHGOA_IEEE |
| UI | Analyst dashboard, conversational interface, or case-management interface |

## Optional
- LangGraph
- LangChain
- OpenAI Agents SDK
- CrewAI
- Custom agent
- Any suitable LLM
- External APIs/databases/simulated interactions

## Principle
The LLM handles reasoning, tool selection, evidence synthesis, and explanations. TigerGraph/GSQL/graph algorithms handle graph traversal, relationship analysis, and fraud investigation.
