#!/usr/bin/env python3
"""
Step 1: Inspect TigerGraph connection configuration and test connectivity.
- Reads .env without printing secrets.
- Reports which required variables are set or missing.
- Tests the connection to the Savanna workspace.
- Does NOT create or modify any graph.
"""
import os
import sys

ENV_PATH = "D:/task4/.env"

def parse_env(path):
    env_vars = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                env_vars[key.strip()] = val.strip()
    return env_vars

def mask(val):
    if not val:
        return "(empty)"
    if len(val) <= 8:
        return "[SET]"
    return f"[SET ({len(val)} chars)]"

env_vars = parse_env(ENV_PATH)
print("=" * 60)
print("TIGERGRAPH CONNECTION CONFIGURATION INSPECTION")
print("=" * 60)

# ---- Required variables (primary TG_* convention + legacy TIGERGRAPH_* alias) ----
# mcp/config.py resolves these with fallbacks
required_vars = [
    ("TG_HOST",          "TG_HOST or TIGERGRAPH_HOST", env_vars.get("TG_HOST") or env_vars.get("TIGERGRAPH_HOST")),
    ("TG_GRAPHNAME",     "TG_GRAPHNAME or TIGERGRAPH_GRAPH_NAME", env_vars.get("TG_GRAPHNAME") or env_vars.get("TIGERGRAPH_GRAPH_NAME")),
    ("TG_USERNAME",      "TG_USERNAME or TIGERGRAPH_USERNAME", env_vars.get("TG_USERNAME") or env_vars.get("TIGERGRAPH_USERNAME")),
    ("TG_PASSWORD",      "TG_PASSWORD or TIGERGRAPH_PASSWORD", env_vars.get("TG_PASSWORD") or env_vars.get("TIGERGRAPH_PASSWORD")),
    ("TG_SECRET",        "TG_SECRET or TIGERGRAPH_SECRET", env_vars.get("TG_SECRET") or env_vars.get("TIGERGRAPH_SECRET")),
    ("TG_TGCLOUD",       "TG_TGCLOUD", env_vars.get("TG_TGCLOUD")),
    ("TG_PORT/SSL",      "TG_SSL_PORT/TG_PORT/TIGERGRAPH_PORT", env_vars.get("TG_SSL_PORT") or env_vars.get("TG_PORT") or env_vars.get("TIGERGRAPH_PORT")),
    ("TG_API_TOKEN",     "TG_API_TOKEN or TG_TOKEN", env_vars.get("TG_API_TOKEN") or env_vars.get("TG_TOKEN")),
]

print("\n--- Required Environment Variables ---")
print(f"{'Variable':<30} {'Status':<12} {'Source':<30}")
print("-" * 72)
all_set = True
for var_name, display_name, value in required_vars:
    status = "SET" if value else "MISSING"
    if not value:
        all_set = False
    source = ""
    for k in [var_name, "TG_HOST", "TIGERGRAPH_HOST"]:
        if k in env_vars and env_vars[k]:
            if k == var_name or (var_name in ("TG_HOST",) and k in ("TG_HOST", "TIGERGRAPH_HOST")) or display_name in k:
                source = k
                break
    # Find which env key provided the value
    found_key = ""
    for k, v in env_vars.items():
        if v == value and value:
            found_key = k
            break
    print(f"  {var_name:<28} {status:<12} {found_key or '-'}")

print(f"\n  All required variables set: {all_set}")

# ---- Print non-sensitive config ----
print("\n--- Non-Sensitive Configuration ---")
print(f"  Host:     {env_vars.get('TG_HOST', 'NOT SET')}")
print(f"  Graph:    {env_vars.get('TG_GRAPHNAME') or env_vars.get('TIGERGRAPH_GRAPH_NAME') or 'NOT SET'}")
print(f"  Username: {env_vars.get('TG_USERNAME') or env_vars.get('TIGERGRAPH_USERNAME') or 'NOT SET'}")
print(f"  TGCLOUD:  {env_vars.get('TG_TGCLOUD', 'NOT SET')}")
print(f"  Port:     {env_vars.get('TG_SSL_PORT') or env_vars.get('TG_PORT') or env_vars.get('TIGERGRAPH_PORT', 'NOT SET')}")

# ---- Connection test ----
print("\n--- Connection Test ---")
if not all_set:
    print("  SKIPPED: Required variables are missing.")
    print(f"\n  TIGERGRAPH CONNECTION: FAIL")
    sys.exit(1)

try:
    from pyTigerGraph import TigerGraphConnection

    host = env_vars["TG_HOST"]
    graphname = env_vars.get("TG_GRAPHNAME") or env_vars.get("TIGERGRAPH_GRAPH_NAME")
    username = env_vars["TG_USERNAME"]
    password = env_vars["TG_PASSWORD"]
    secret = env_vars.get("TG_SECRET") or env_vars.get("TIGERGRAPH_SECRET")
    ssl_port = int(env_vars.get("TG_SSL_PORT") or env_vars.get("TG_PORT") or env_vars.get("TIGERGRAPH_PORT") or "443")

    conn = TigerGraphConnection(
        host=host,
        graphname=graphname,
        gsqlSecret=secret,
        username=username,
        password=password,
        tgCloud=True,
        sslPort=ssl_port,
    )
    print("  Connection object created.")

    # Test token creation with the secret
    try:
        token = conn.getToken(secret, "100000")
        if token and len(token) > 0:
            print(f"  Token: OBTAINED (truncated: {token[0][:20]}...)")
        else:
            print("  Token: FAILED to obtain (None/empty)")
    except Exception as e:
        err = str(e)
        print(f"  Token: FAILED - {type(e).__name__}: {err[:200]}")

    # Test echo (RESTPP reachable)
    try:
        echo = conn.echo()
        print(f"  Echo: {echo}")
    except Exception as e:
        print(f"  Echo: FAILED - {type(e).__name__}: {str(e)[:200]}")

    # Test version
    try:
        ver = conn.getVersion()
        print(f"  Version: {ver}")
    except Exception as e:
        print(f"  Version: FAILED - {type(e).__name__}: {str(e)[:200]}")

    # List graphs
    try:
        graphs = conn.listGraphs()
        print(f"  Available graphs: {graphs}")
        graph_exists = graphname in graphs
        print(f"  Graph '{graphname}' exists: {graph_exists}")
    except Exception as e:
        print(f"  List graphs: FAILED - {type(e).__name__}: {str(e)[:200]}")
        graph_exists = False

    print(f"\n  TIGERGRAPH CONNECTION: PASS")

except Exception as e:
    print(f"\n  TIGERGRAPH CONNECTION: FAIL")
    print(f"  Error: {type(e).__name__}: {str(e)[:500]}")
    sys.exit(1)
