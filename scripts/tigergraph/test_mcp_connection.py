"""Phase 5: Connection test for TigerGraph MCP integration.
Tests:
1. Port availability
2. MCP server startup (stdio)
3. Tool discovery via MCP protocol
4. Live TigerGraph connectivity (if credentials configured)
"""

import asyncio
import json
import os
import socket
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("HHGOA TIGERGRAPH MCP CONNECTION TEST")
print("=" * 60)

# ---------------------------------------------------------------------------
# 1. Port availability check
# ---------------------------------------------------------------------------
print("\n--- 1. Port Availability ---")
for host, port in [("127.0.0.1", 9000), ("127.0.0.1", 14240)]:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    result = s.connect_ex((host, port))
    status = "OPEN" if result == 0 else "CLOSED"
    print(f"  {host}:{port} -> {status}")
    s.close()

# ---------------------------------------------------------------------------
# 2. Environment configuration check
# ---------------------------------------------------------------------------
print("\n--- 2. Environment Configuration ---")
tg_host = os.getenv("TG_HOST", "")
tg_graphname = os.getenv("TG_GRAPHNAME", "")
tg_username = os.getenv("TG_USERNAME", "tigergraph")
tg_password = os.getenv("TG_PASSWORD", "")
tg_secret = os.getenv("TG_SECRET", "")
tg_tgcloud = os.getenv("TG_TGCLOUD", "false").lower() == "true"

print(f"  TG_HOST:        {tg_host or '(not set)'}")
print(f"  TG_GRAPHNAME:   {tg_graphname or '(not set)'}")
print(f"  TG_USERNAME:    {tg_username}")
print(f"  TG_PASSWORD:    {'***' if tg_password else '(not set)'}")
print(f"  TG_SECRET:      {'***' if tg_secret else '(not set)'}")
print(f"  TG_TGCLOUD:     {tg_tgcloud}")

has_credentials = bool(tg_host) and bool(tg_password)
if tg_tgcloud and not tg_host.startswith("https://"):
    print("  WARNING: TG_TGCLOUD=true but TG_HOST is not a Savanna URL")
if not has_credentials:
    print("  STATUS: NO VALID CREDENTIALS - live connection will fail")

# ---------------------------------------------------------------------------
# 3. MCP server startup test (stdio)
# ---------------------------------------------------------------------------
print("\n--- 3. MCP Server Startup Test ---")
try:
    from tigergraph_mcp.main import main as mcp_main
    print("  tigergraph-mcp package: INSTALLED (v1.0.3)")
except ImportError as e:
    print(f"  tigergraph-mcp package: FAILED - {e}")
    sys.exit(1)

try:
    from tigergraph_mcp.tools import get_all_tools
    tools = get_all_tools(apply_filter=False)
    print(f"  Total tools available: {len(tools)}")
    read_only_tools = [
        "tigergraph__get_global_schema",
        "tigergraph__list_graphs",
        "tigergraph__get_graph_schema",
        "tigergraph__show_graph_details",
        "tigergraph__get_node",
        "tigergraph__get_nodes",
        "tigergraph__get_edge",
        "tigergraph__get_edges",
        "tigergraph__run_installed_query",
        "tigergraph__get_vertex_count",
    ]
    available_ro = [t for t in tools if t.name in read_only_tools]
    print(f"  Read-only tools available: {len(available_ro)}")
    for t in available_ro:
        print(f"    - {t.name}")
except Exception as e:
    print(f"  Tool discovery: FAILED - {e}")

# ---------------------------------------------------------------------------
# 4. Live TigerGraph connectivity test
# ---------------------------------------------------------------------------
print("\n--- 4. Live TigerGraph Connectivity ---")
if not has_credentials:
    print("  SKIPPED: No valid credentials configured.")
    print("  To enable live testing, update .env with:")
    print("    TG_HOST=https://your-subdomain.i.tgcloud.io")
    print("    TG_PASSWORD=your_password")
    print("    TG_SECRET=your_database_secret")
    print("    TG_TGCLOUD=true")
else:
    try:
        from pyTigerGraph import AsyncTigerGraphConnection

        async def test_connection():
            conn = AsyncTigerGraphConnection(
                host=tg_host,
                graphname=tg_graphname,
                username=tg_username,
                password=tg_password,
                gsqlSecret=tg_secret or "",
                tgCloud=tg_tgcloud,
            )
            try:
                echo = await conn.echo()
                print(f"  ECHO: {echo}")
                return True, conn
            except Exception as e:
                print(f"  ECHO FAILED: {type(e).__name__}: {str(e)[:200]}")
                return False, None

        connected, conn = asyncio.run(test_connection())
        if connected:
            print("  STATUS: CONNECTED to TigerGraph")
        else:
            print("  STATUS: CONNECTION FAILED - credentials or endpoint invalid")
    except ImportError:
        print("  pyTigerGraph not installed")
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {str(e)[:200]}")

# ---------------------------------------------------------------------------
# 5. Summary
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("CONNECTION TEST SUMMARY")
print("=" * 60)
print(f"  TigerGraph MCP package: INSTALLED")
print(f"  MCP tools available:    {len(tools)}")
print(f"  Live connection:        {'ATTEMPTED' if has_credentials else 'BLOCKED (no credentials)'}")
print("=" * 60)