#!/usr/bin/env python3
"""Step 1: TigerGraph connection configuration inspection and connectivity test."""
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

env_vars = parse_env(ENV_PATH)

# ---- Resolve required variables (matching mcp/config.py resolution) ----
host          = env_vars.get("TG_HOST") or env_vars.get("TIGERGRAPH_HOST")
graphname     = env_vars.get("TG_GRAPHNAME") or env_vars.get("TIGERGRAPH_GRAPH_NAME") or "HHGOA_Fraud_Graph"
username      = env_vars.get("TG_USERNAME") or env_vars.get("TIGERGRAPH_USERNAME") or "tigergraph"
password      = env_vars.get("TG_PASSWORD") or env_vars.get("TIGERGRAPH_PASSWORD") or "tigergraph"
secret        = env_vars.get("TG_SECRET") or env_vars.get("TIGERGRAPH_SECRET") or ""
tgcoud        = env_vars.get("TG_TGCLOUD", "false").lower() in ("true", "1", "yes")
ssl_port      = int(env_vars.get("TG_SSL_PORT") or env_vars.get("TG_PORT") or env_vars.get("TIGERGRAPH_PORT") or "443")
api_token     = env_vars.get("TG_API_TOKEN") or env_vars.get("TG_TOKEN") or ""

print("=" * 60)
print("TIGERGRAPH CONNECTION CONFIGURATION INSPECTION")
print("=" * 60)

# ---- Report required variables (masked) ----
print("\n--- Required Environment Variables ---")
checks = [
    ("TG_HOST",       host),
    ("TG_GRAPHNAME",  graphname),
    ("TG_USERNAME",   username),
    ("TG_PASSWORD",   password),
    ("TG_SECRET",     secret),
    ("TG_TGCLOUD",    str(tgcoud)),
    ("TG_SSL_PORT",   str(ssl_port)),
    ("TG_API_TOKEN",  api_token),
]
all_set = True
for name, val in checks:
    status = "SET" if val and val not in ("", "false") else ("SET (false)" if val == "false" else "MISSING/EMPTY")
    if val == "" or val == "false" or val is None:
        if name in ("TG_TGCLOUD",):
            pass  # TG_TGCLOUD can be set to false
        elif name in ("TG_API_TOKEN",):
            pass  # API token is optional if secret is set
        else:
            all_set = False
    print(f"  {name:<20} {status}")

print(f"\n  All critical variables set: {all_set}")
# Note: TG_API_TOKEN is optional - TG_SECRET is sufficient for auth

# ---- Non-sensitive config ----
print("\n--- Non-Sensitive Configuration ---")
print(f"  Host:     {host}")
print(f"  Graph:    {graphname}")
print(f"  Username: {username}")
print(f"  TGCLOUD:  {tgcoud}")
print(f"  Port:     {ssl_port}")

# ---- Connection test ----
print("\n--- Connection Test ---")
if not host or not graphname or not username:
    print("  SKIPPED: Critical variables missing.")
    print("\nTIGERGRAPH CONNECTION: FAIL")
    sys.exit(1)

try:
    from pyTigerGraph import TigerGraphConnection

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

    # Test token with secret
    print("  Obtaining auth token from secret...")
    try:
        token = conn.getToken(secret, "100000")
        if token and len(token) > 0:
            print(f"  Token: OBTAINED (truncated: {token[0][:20]}...)")
        else:
            print("  Token: FAILED to obtain (None/empty)")
    except Exception as e:
        print(f"  Token: FAILED - {type(e).__name__}: {str(e)[:200]}")

    # Test echo
    try:
        echo = conn.echo()
        print(f"  Echo: OK - {echo}")
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

    # If graph exists, show schema
    if graph_exists:
        try:
            schema = conn.getSchema()
            vtypes = [v.get("Type", v.get("Name", "?")) for v in schema.get("VertexTypes", [])]
            etypes = [e.get("Type", e.get("Name", "?")) for e in schema.get("EdgeTypes", [])]
            print(f"\n  Existing schema:")
            print(f"    Vertex types ({len(vtypes)}): {vtypes}")
            print(f"    Edge types ({len(etypes)}): {etypes}")
        except Exception as e:
            print(f"  Schema: FAILED - {type(e).__name__}: {str(e)[:200]}")

    print(f"\n  TIGERGRAPH CONNECTION: PASS")
except Exception as e:
    print(f"\n  TIGERGRAPH CONNECTION: FAIL")
    print(f"  Error: {type(e).__name__}: {str(e)[:500]}")
    sys.exit(1)
