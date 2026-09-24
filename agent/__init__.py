"""HHGOA AI Investigator Agent.

A minimal, demo-ready autonomous fraud investigation agent that sits on top
of the existing HHGOA TigerGraph MCP server (see ``mcp/``).

The agent accepts a transaction ID, drives the seven existing MCP
investigation tools, aggregates the normalized evidence, and produces a
structured investigation report:

    python -m agent.investigator 3514030

Environment variables:

    GEMINI_API_KEY   Gemini API key. When present the agent runs the
                     Gemini function-calling loop; otherwise it falls back
                     to a deterministic local deliberative engine built on
                     the exact same MCP tools. The key is never printed.
    GEMINI_MODEL     Optional model override (default: gemini-2.5-flash).
    TG_MOCK_MODE     true  -> use verified offline TigerGraph fixtures
                     false -> use the live TigerGraph cluster
"""

__version__ = "1.0.0"
__all__ = ["Investigator", "InvestigationReport", "render_report"]

# Lazy re-exports so importing `agent` does not pull in the MCP stack
# until an agent object is actually requested.


def __getattr__(name):
    if name in ("Investigator", "render_report"):
        from .investigator import Investigator, render_report

        return {"Investigator": Investigator, "render_report": render_report}[name]
    if name == "InvestigationReport":
        from .models import InvestigationReport

        return InvestigationReport
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
