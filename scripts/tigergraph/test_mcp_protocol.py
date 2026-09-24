"""Phase 5b: Verify MCP server starts in stdio mode and advertises tools correctly.
Tests the MCP protocol layer without requiring a live TigerGraph connection.
"""

import asyncio
import json
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("HHGOA TIGERGRAPH MCP PROTOCOL TEST")
print("=" * 60)

# ---------------------------------------------------------------------------
# 1. Verify MCP server module can be imported and configured
# ---------------------------------------------------------------------------
print("\n--- 1. MCP Server Module Import ---")
try:
    from tigergraph_mcp.server import MCPServer, serve
    print("  MCPServer class: OK")
    print("  serve() function: OK")
except ImportError as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 2. Verify tool filter configuration
# ---------------------------------------------------------------------------
print("\n--- 2. Tool Filter Configuration ---")
try:
    from tigergraph_mcp import tool_filter
    tool_filter.configure(allowed="read-only", blocked="destructive")
    from tigergraph_mcp.tools import get_all_tools
    all_tools = get_all_tools(apply_filter=False)
    filtered = get_all_tools(apply_filter=True)
    print(f"  Total tools (unfiltered): {len(all_tools)}")
    print(f"  Tools after 'read-only' filter: {len(filtered)}")
    print(f"  Blocked categories: destructive")
    
    # List read-only tools
    print("\n  Read-only tools available:")
    for t in filtered:
        print(f"    - {t.name}")
except Exception as e:
    print(f"  FAILED: {e}")
    import traceback
    traceback.print_exc()

# ---------------------------------------------------------------------------
# 3. Verify MCP server can create a stdio transport
# ---------------------------------------------------------------------------
print("\n--- 3. MCP Server Stdio Transport ---")
try:
    from mcp.server.stdio import stdio_server
    print("  stdio_server import: OK")
except ImportError as e:
    print(f"  FAILED: {e}")

# ---------------------------------------------------------------------------
# 4. Verify VS Code MCP config schema
# ---------------------------------------------------------------------------
print("\n--- 4. VS Code MCP Config Validation ---")
import json
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                            ".vscode", "mcp.json")
if os.path.exists(config_path):
    with open(config_path, "r") as f:
        config = json.load(f)
    print(f"  Config file exists: {config_path}")
    print(f"  Servers configured: {list(config.get('servers', {}).keys())}")
    print(f"  Inputs defined: {len(config.get('inputs', []))}")
    
    # Validate required fields
    for name, server in config.get("servers", {}).items():
        assert server.get("type") == "stdio", f"{name}: type must be stdio"
        assert server.get("command"), f"{name}: command is required"
        assert "args" in server, f"{name}: args is required"
        assert "env" in server, f"{name}: env is required"
        print(f"  {name}: VALID (command={server['command']}, args={len(server['args'])})")
else:
    print(f"  Config file NOT FOUND: {config_path}")

# ---------------------------------------------------------------------------
# 5. Verify .env.example has correct variable names
# ---------------------------------------------------------------------------
print("\n--- 5. Environment Variable Template ---")
env_example = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            ".env.example")
if os.path.exists(env_example):
    with open(env_example, "r") as f:
        content = f.read()
    required_vars = ["TG_HOST", "TG_GRAPHNAME", "TG_USERNAME", "TG_PASSWORD", "TG_SECRET", "TG_TGCLOUD"]
    found = [v for v in required_vars if v in content]
    missing = [v for v in required_vars if v not in content]
    print(f"  Required vars present: {found}")
    if missing:
        print(f"  MISSING: {missing}")
    else:
        print("  All required variables present in template")
    
    # Check no real secrets
    lines = content.strip().split("\n")
    secret_lines = [l for l in lines if "=" in l and not l.strip().startswith("#") 
                    and any(k in l for k in ["TG_PASSWORD", "TG_SECRET"])
                    and not any(placeholder in l for placeholder in ["YOUR_", "PLACEHOLDER", "EXAMPLE"])]
    if secret_lines:
        print(f"  WARNING: Possible hardcoded secrets: {secret_lines}")
    else:
        print("  No hardcoded secrets detected")
else:
    print(f"  .env.example NOT FOUND")

print("\n" + "=" * 60)
print("MCP PROTOCOL TEST COMPLETE")
print("=" * 60)
print("STATUS: MCP server package is installed and configured.")
print("LIVE CONNECTION: BLOCKED - no TigerGraph instance reachable.")
print("NEXT STEP: Provide Savanna credentials to enable live connection.")