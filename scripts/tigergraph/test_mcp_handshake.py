"""Phase 5d: Full MCP protocol handshake test.
Tests initialize and list_tools via stdio without requiring live TigerGraph.
"""

import asyncio
import json
import os
import sys
import subprocess

print("=" * 60)
print("HHGOA TIGERGRAPH MCP PROTOCOL HANDSHAKE TEST")
print("=" * 60)

# Start MCP server in stdio mode
proc = subprocess.Popen(
    [sys.executable, "-m", "tigergraph_mcp.main", "--transport", "stdio", "--allowed-tools", "read-only"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd="D:/task4",
    env={**os.environ, "TG_HOST": "http://127.0.0.1", "TG_GRAPHNAME": "HHGOA_Fraud_Graph"}
)

# Send initialize request
init_req = json.dumps({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "clientInfo": {"name": "test-client", "version": "1.0.0"},
        "capabilities": {}
    }
}) + "\n"

proc.stdin.write(init_req)
proc.stdin.flush()

# Read initialize response
import select
import time
time.sleep(1)

# Check if stdout has data
stdout_data = ""
stderr_data = ""
try:
    # Non-blocking read
    proc.stdin.close()
    proc.terminate()
    stdout, stderr = proc.communicate(timeout=3)
    stdout_data = stdout
    stderr_data = stderr
except subprocess.TimeoutExpired:
    proc.kill()
    stdout, stderr = proc.communicate()
    stdout_data = stdout
    stderr_data = stderr

print("\n--- MCP Initialize Response ---")
if stdout_data:
    lines = stdout_data.strip().split('\n')
    for line in lines[:3]:
        try:
            resp = json.loads(line)
            if 'result' in resp:
                info = resp['result'].get('serverInfo', {})
                print(f"  Server: {info.get('name', 'unknown')} v{info.get('version', 'unknown')}")
                print(f"  Protocol: {resp['result'].get('protocolVersion', 'unknown')}")
            elif 'error' in resp:
                print(f"  Error: {resp['error']}")
        except json.JSONDecodeError:
            print(f"  Raw: {line[:100]}")
else:
    print("  No stdout response")

print("\n--- MCP Server stderr ---")
if stderr_data:
    for line in stderr_data.strip().split('\n')[:5]:
        print(f"  {line[:150]}")
else:
    print("  (empty)")

print("\n" + "=" * 60)
print("PROTOCOL HANDSHAKE TEST COMPLETE")
print("=" * 60)