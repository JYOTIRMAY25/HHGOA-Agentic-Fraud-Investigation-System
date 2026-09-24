#!/usr/bin/env python3
"""Deploy HHGOA schema to TigerGraph Savanna."""
import os, re, sys
from dotenv import load_dotenv
load_dotenv('D:/task4/.env')
from pyTigerGraph import TigerGraphConnection

host = os.getenv('TG_HOST')
graphname = os.getenv('TG_GRAPH')
username = os.getenv('TG_USERNAME')
password = os.getenv('TG_PASSWORD')
secret = os.getenv('TG_SECRET')

conn = TigerGraphConnection(host=host, graphname=graphname, gsqlSecret=secret, username=username, password=password, tgCloud=True, sslPort=443)

# Parse schema file into statements (respecting bracket depth)
with open('tigergraph/schema/schema.gsql') as f:
    content = f.read()

# Remove comments
content_no_comments = re.sub(r'//.*', '', content)

# Split into statements using keyword boundaries
STATEMENT_STARTERS = [
    'DROP GRAPH', 'CREATE GRAPH', 'USE GRAPH',
    'CREATE VERTEX', 'CREATE DIRECTED EDGE', 'CREATE EDGE',
    'CREATE QUERY', 'INTERPRET QUERY', 'ALTER',
]

statements = []
current = None
for line in content_no_comments.split('\n'):
    stripped = line.strip()
    if stripped == '':
        continue
    is_new = any(stripped.startswith(s) for s in STATEMENT_STARTERS)
    if is_new:
        if current is not None:
            statements.append(current)
        current = stripped
    else:
        if current is not None:
            current += ' ' + stripped
if current is not None:
    statements.append(current)

# Add semicolons where needed
formatted = []
for s in statements:
    if not s.endswith(';'):
        s += ';'
    formatted.append(s)

print(f"Parsed {len(formatted)} statements\n")

# Pre-deployment: drop graph if exists
try:
    conn.gsql('DROP GRAPH HHGOA_Fraud_Graph')
    print("Dropped existing graph\n")
except:
    print("No existing graph to drop\n")

# Create graph
try:
    r = conn.gsql('CREATE GRAPH HHGOA_Fraud_Graph()')
    print(f"CREATE GRAPH: {r}")
except Exception as e:
    print(f"CREATE GRAPH ERROR: {e}")

# Use graph
try:
    r = conn.gsql('USE GRAPH HHGOA_Fraud_Graph')
    print(f"USE GRAPH: {r}")
except Exception as e:
    print(f"USE GRAPH ERROR: {e}")

# Deploy remaining statements
print("\n--- Deploying Schema ---\n")
results = []
for i, stmt in enumerate(formatted):
    if stmt.startswith('DROP GRAPH') or stmt.startswith('CREATE GRAPH') or stmt.startswith('USE GRAPH'):
        results.append(("SKIP", stmt[:50], ""))
        continue
    try:
        r = conn.gsql(stmt)
        results.append(("PASS", stmt[:50], str(r)[:100]))
        print(f"  [{i+1}/{len(formatted)}] PASS: {stmt[:60]}")
    except Exception as e:
        err = f"{type(e).__name__}: {str(e)[:150]}"
        results.append(("FAIL", stmt[:50], err))
        print(f"  [{i+1}/{len(formatted)}] FAIL: {stmt[:60]}")
        print(f"    -> {err}")

# Summary
print("\n" + "=" * 60)
passed = sum(1 for r in results if r[0] == "PASS")
failed = sum(1 for r in results if r[0] == "FAIL")
print(f"PASS: {passed}, FAIL: {failed}")
