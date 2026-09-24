#!/usr/bin/env python3
"""Fix type error and install query."""
import os
from dotenv import load_dotenv
load_dotenv('D:/task4/.env')
from pyTigerGraph import TigerGraphConnection

host = os.getenv('TG_HOST')
graphname = os.getenv('TG_GRAPH')
username = os.getenv('TG_USERNAME')
password = os.getenv('TG_PASSWORD')
secret = os.getenv('TG_SECRET')

conn = TigerGraphConnection(host=host, graphname=graphname, gsqlSecret=secret, username=username, password=password, tgCloud=True, sslPort=443)
conn.useGraph(graphname)

# Fix 1: ALTER vertex to add transaction_id as explicit attribute (in case PRIMARY_ID doesn't expose it properly)
print("Attempting ALTER VERTEX to add attribute...")
try:
    r = conn.gsql(f"ALTER VERTEX Transaction ADD ATTRIBUTES (transaction_id STRING)")
    print(f"ALTER VERTEX: {r}")
except Exception as e:
    print(f"ALTER VERTEX error: {type(e).__name__}: {str(e)[:300]}")

# Fix 2: Drop and recreate query with explicit attribute reference
print("\nDeploying fixed query...")
query = (
    f"USE GRAPH {graphname}\n"
    f"CREATE OR REPLACE QUERY shortestPath(STRING start_txn_id, STRING end_txn_id) FOR GRAPH {graphname} {{\n"
    f"    ListAccum<STRING> @@path;\n"
    f"    Start = {{Transaction.*}};\n"
    f"    Src = SELECT s FROM Start:s WHERE s.transaction_id == start_txn_id;\n"
    f"    Tgt = SELECT t FROM Src:s -(NEXT_TRANSACTION:e)-> t WHERE t.transaction_id == end_txn_id\n"
    f"        ACCUM @@path += t.transaction_id;\n"
    f"    PRINT @@path AS path;\n"
    f"}}"
)
try:
    r = conn.gsql(query)
    print(f"Deploy result: {str(r)[:500]}")
except Exception as e:
    print(f"Deploy error: {type(e).__name__}: {str(e)[:300]}")

# Check status
print("\nChecking status...")
try:
    r = conn.getQueryInfo("shortestPath")
    status = r.get('results', [{}])[0].get('status', 'UNKNOWN')
    installed = r.get('results', [{}])[0].get('installed', False)
    error = r.get('results', [{}])[0].get('error', True)
    print(f"Status: {status}, Installed: {installed}, Error: {error}")
except Exception as e:
    print(f"Status check error: {type(e).__name__}: {str(e)[:200]}")

# Try to install
print("\nTrying install...")
try:
    r = conn.installQueries("shortestPath")
    print(f"Install: {r}")
except Exception as e:
    print(f"Install error: {type(e).__name__}: {str(e)[:300]}")
