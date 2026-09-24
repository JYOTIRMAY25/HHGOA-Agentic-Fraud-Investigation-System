"""Phase 5e (fixed): Full MCP protocol test using the MCP SDK client.
Tests initialize + list_tools via stdio without requiring live TigerGraph.
"""

import asyncio
import json
import os
import sys

print("=" * 60)
print("HHGOA TIGERGRAPH MCP SDK CLIENT TEST")
print("=" * 60)

async def test_mcp():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "tigergraph_mcp.main", "--transport", "stdio", "--allowed-tools", "read-only"],
        env={**os.environ, "TG_HOST": "http://127.0.0.1", "TG_GRAPHNAME": "HHGOA_Fraud_Graph"}
    )
    
    print("\n--- 1. Connecting to MCP server ---")
    try:
        async with stdio_client(server_params) as (read, write):
            print("  Stdio transport: CONNECTED")
            
            async with ClientSession(read, write) as session:
                print("  Client session: ESTABLISHED")
                
                # Initialize
                print("\n--- 2. MCP Initialize ---")
                init_result = await session.initialize()
                print(f"  Server: {init_result.serverInfo.name} v{init_result.serverInfo.version}")
                print(f"  Capabilities: {init_result.capabilities}")
                
                # List tools
                print("\n--- 3. List Tools ---")
                tools_result = await session.list_tools()
                tools = tools_result.tools
                print(f"  Total tools advertised: {len(tools)}")
                
                # Show key investigation tools
                key_tools = [
                    "tigergraph__get_graph_schema",
                    "tigergraph__list_graphs",
                    "tigergraph__get_global_schema",
                    "tigergraph__get_vertex_count",
                    "tigergraph__get_edge_count",
                    "tigergraph__get_node",
                    "tigergraph__get_nodes",
                    "tigergraph__get_edge",
                    "tigergraph__get_edges",
                    "tigergraph__run_installed_query",
                    "tigergraph__show_graph_details",
                ]
                print("\n  Key investigation tools available:")
                for t in tools:
                    if t.name in key_tools:
                        desc = t.description[:80] if t.description else 'N/A'
                        print(f"    - {t.name}: {desc}")
                
                print("\n  All tool names:")
                for t in tools:
                    print(f"    - {t.name}")
                
                return True
                
    except Exception as e:
        print(f"  FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

success = asyncio.run(test_mcp())

print("\n" + "=" * 60)
print("MCP SDK CLIENT TEST RESULT")
print("=" * 60)
print(f"MCP Protocol: {'WORKING' if success else 'FAILED'}")
print(f"VS Code MCP config: CREATED at .vscode/mcp.json")
print(f"Live TigerGraph: BLOCKED (no instance reachable)")
print("=" * 60)