"""
HHGOA TigerGraph MCP Server
Builds the MCP tool registration layer around the existing investigation functions.

The installed MCP SDK (mcp 2.x) lives in site-packages, but this project's local
`mcp` package shadows it. We load the SDK by temporarily removing our local
package from sys.path, importing the SDK symbols, then restoring our package.
This keeps the local mcp.* imports intact while still using the real SDK.
"""

import os
import sys
import importlib
import logging
import json

logger = logging.getLogger("mcp.server")


def _load_sdk_symbols():
    """Import the installed MCP SDK symbols without our local mcp package shadowing.

    Returns a tuple of (MCPServer, stdio_server, Tool, TextContent, CallToolResult).
    The SDK is loaded fresh each call; the local mcp package is fully restored
    afterwards so all subsequent `from mcp.* import ...` statements resolve to
    our project code.
    """
    our_package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    our_package_dir = os.path.realpath(our_package_dir)

    # Snapshot our local mcp package and submodules so we can restore them.
    saved_modules = {}
    for key in list(sys.modules):
        if key == "mcp" or key.startswith("mcp."):
            saved_modules[key] = sys.modules.pop(key)

    saved_path = sys.path[:]

    # Remove our local package directory from the search path so the SDK in
    # site-packages is the one that gets imported.
    sys.path = [p for p in sys.path
                if os.path.realpath(p) != our_package_dir and p != ""]

    # Also clear the SDK's own modules in case a previous partial load lingers.
    for key in list(sys.modules):
        if key == "mcp" or key.startswith("mcp.") or key == "mcp_types" or key.startswith("mcp_types."):
            del sys.modules[key]

    try:
        from mcp.server.mcpserver import MCPServer
        from mcp.server.mcpserver.server import Settings
        from mcp.server.mcpserver.tools import Tool
        from mcp.server.stdio import stdio_server
        from mcp.types import TextContent, CallToolResult
        # Rebuild Pydantic model to resolve forward references
        Settings.model_rebuild()
        return MCPServer, stdio_server, Tool, TextContent, CallToolResult
    finally:
        # Purge every SDK module that was loaded during the import so that
        # later `import mcp.*` resolves to our local package again.
        for key in list(sys.modules):
            if key == "mcp" or key.startswith("mcp.") or key == "mcp_types" or key.startswith("mcp_types."):
                if key not in saved_modules:
                    del sys.modules[key]
        sys.path = saved_path
        # Restore our local mcp package (and any submodules that were already
        # loaded before this function ran).
        sys.modules.update(saved_modules)
        # Make sure the local mcp package is the one in sys.modules.
        if "mcp" not in sys.modules:
            importlib.import_module("mcp")


# Load the SDK symbols at module import time.
MCPServer, stdio_server, Tool, TextContent, CallToolResult = _load_sdk_symbols()

# Now import our project's investigation layer (resolves to local mcp package).
from mcp.config import MCPConfig
from mcp.connection import default_connection, TigerGraphConnectionError
from mcp.tools.investigation import (
    execute_investigate_transaction,
    execute_trace_connected_entities,
    execute_detect_card_testing,
    execute_analyze_region_anomalies,
    execute_retrieve_similar_cases,
    execute_calculate_case_exposure,
    execute_validate_graph_metrics,
)
from mcp.tools.validation import ValidationError


# Tool descriptions for MCP registration
TOOL_DESCRIPTIONS = {
    "investigate_transaction": (
        "Investigates a single transaction by ID. Returns the transaction record, "
        "associated card and customer details, device profile, purchaser/recipient emails, "
        "billing regions, and any prior fraud cases linked to this transaction. "
        "Risk signals (elevated model score, new device, anonymous proxy) are investigation "
        "signals, not automatic fraud verdicts. Use to begin a transaction-level investigation."
    ),
    "trace_connected_entities": (
        "Traces entities connected to a target card up to max_hops (1-3). Discovers other cards "
        "owned by the same customer, shared devices, and syndicate links via shared devices. "
        "Returns connected entities with hop distance and connection path (SAME_CUSTOMER, USED_DEVICE, "
        "SHARED_DEVICE_SYNDICATE). Cross-account device sharing (SHARED_DEVICE_SYNDICATE) is a "
        "CRITICAL risk signal per Policy Rule R6, but requires analyst confirmation before action."
    ),
    "detect_card_testing": (
        "Detects card testing patterns (micro-authorizations followed by larger charge) for a card "
        "within a time window. Parameters: window_minutes (10-1440, default 60), micro_threshold "
        "(0.5-50 USD, default 5.0), min_micro_attempts (1-10, default 3). Returns detection result, "
        "micro-authorization count, subsequent large charge amount, and transaction sequence. "
        "A confirmed card testing burst (3+ micros then large charge) is a CRITICAL signal per Policy "
        "Rule R5 prescribing DECLINE_TRANSACTION and STEP_UP_AUTH, but is not an automatic fraud verdict."
    ),
    "analyze_region_anomalies": (
        "Analyzes geographic dispersion of a card's transactions. Returns total transaction count, "
        "region distribution, distinct region count, and international (out-of-region) transaction count. "
        "International use is a HIGH severity signal; multi-region activity is MEDIUM. These are "
        "investigation signals to distinguish sustained travel from card cloning (README line 119), "
        "not automatic fraud verdicts."
    ),
    "retrieve_similar_cases": (
        "Retrieves historical fraud cases similar to the investigation subject. At least one of "
        "customer_id, card_id, or pattern_id must be provided. Valid pattern_id values: "
        "card_testing, card_not_present_fraud, card_not_present_new_device, out_of_region_use, "
        "account_takeover, undocumented, none. Returns precedent cases with outcome, exposure, "
        "actions taken, analyst notes, and match reason (SAME_CUSTOMER_PRECEDENT, etc.). "
        "Precedents guide investigation but do not determine current case outcome."
    ),
    "calculate_case_exposure": (
        "Calculates total financial exposure for a fraud case. Returns total exposure USD, fraud "
        "transaction count, transaction IDs, and required approval route (auto, L1, L2). "
        "Exposure > $2,500 triggers CRITICAL signal requiring Fraud Manager (L2) approval for card "
        "blocking (Policy Section 2). Exposure > $1,000 triggers HIGH signal mandating FILE_REPORT "
        "if fraud confirmed (Policy Rule R2 / Section 3a). These are policy thresholds for "
        "escalation, not automatic fraud determinations."
    ),
    "validate_graph_metrics": (
        "Validates graph loading by returning vertex and edge counts for all types. Returns counts "
        "for customers, cards, transactions, device profiles, email domains, billing regions, fraud "
        "cases, fraud patterns, and policy rules. This is a read-only diagnostic tool for verifying "
        "graph integrity. Does not expose sensitive data or perform destructive operations."
    ),
}


def _create_tool_wrapper(func, tool_name: str):
    """Create an async wrapper for the synchronous investigation functions."""
    async def wrapper(arguments: dict) -> list[TextContent]:
        try:
            result = func(**arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        except ValidationError as e:
            error_result = {"error": True, "type": "INVALID_PARAMETER", "parameter": e.parameter, "message": str(e)}
            return [TextContent(type="text", text=json.dumps(error_result, indent=2))]
        except TigerGraphConnectionError as e:
            error_result = {"error": True, "type": "CONNECTION_FAILURE", "message": str(e)}
            return [TextContent(type="text", text=json.dumps(error_result, indent=2))]
        except Exception as e:
            error_result = {"error": True, "type": "QUERY_ERROR", "message": f"Unexpected execution error: {str(e)}"}
            return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

    wrapper.__name__ = tool_name
    wrapper.__doc__ = TOOL_DESCRIPTIONS.get(tool_name, "")
    return wrapper


def create_server() -> MCPServer:
    """Create and configure the MCP server with investigation tools."""
    config = MCPConfig()

    # Determine allowed tools based on config
    allowed_tools = set()
    if config.TG_ALLOWED_TOOLS:
        allowed_tools = {t.strip() for t in config.TG_ALLOWED_TOOLS.split(",") if t.strip()}
    else:
        allowed_tools = set(config.DEFAULT_ALLOWED_TOOLS)

    blocked_tools = set(config.BLOCKED_TOOLS)

    # Tool registration functions
    tool_functions = {
        "investigate_transaction": execute_investigate_transaction,
        "trace_connected_entities": execute_trace_connected_entities,
        "detect_card_testing": execute_detect_card_testing,
        "analyze_region_anomalies": execute_analyze_region_anomalies,
        "retrieve_similar_cases": execute_retrieve_similar_cases,
        "calculate_case_exposure": execute_calculate_case_exposure,
        "validate_graph_metrics": execute_validate_graph_metrics,
    }

    # Create MCPServer instance
    server = MCPServer(
        name="hhgoa-tigergraph-fraud-investigation",
        version="1.0.0",
        title="HHGOA TigerGraph Fraud Investigation",
        description=(
            "MCP server for TigerGraph-based fraud investigation. Provides read-only "
            "investigation tools for transaction analysis, entity tracing, card testing "
            "detection, regional anomaly analysis, historical case retrieval, and exposure "
            "calculation. All risk signals are investigation indicators, not automatic "
            "fraud verdicts."
        ),
        tools=[],
    )

    # Register allowed tools
    registered_count = 0
    for tool_name, func in tool_functions.items():
        if tool_name in blocked_tools:
            logger.info("Tool '%s' is blocked by security policy", tool_name)
            continue
        if tool_name not in allowed_tools:
            logger.info("Tool '%s' is not in allowed tools list", tool_name)
            continue

        wrapper = _create_tool_wrapper(func, tool_name)
        tool = server._tool_manager.add_tool(
            fn=wrapper,
            name=tool_name,
            description=TOOL_DESCRIPTIONS.get(tool_name, ""),
        )
        registered_count += 1
        logger.info("Registered MCP tool: %s", tool_name)

    logger.info("MCP server created with %d tools registered", registered_count)
    return server


async def run_server():
    """Run the MCP server with stdio transport."""
    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


def main():
    """Entry point for running the server."""
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_server())


if __name__ == "__main__":
    main()