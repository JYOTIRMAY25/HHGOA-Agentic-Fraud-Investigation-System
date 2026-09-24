#!/usr/bin/env python3
"""Deploy schema to TigerGraph with proper statement parsing."""
import os, re
from dotenv import load_dotenv
load_dotenv('D:/task4/.env')
from pyTigerGraph import TigerGraphConnection

host = os.getenv('TG_HOST')
graphname = os.getenv('TG_GRAPH')
username = os.getenv('TG_USERNAME')
password = os.getenv('TG_PASSWORD')
secret = os.getenv('TG_SECRET')

conn = TigerGraphConnection(host=host, graphname=graphname, gsqlSecret=secret, username=username, password=password, tgCloud=True, sslPort=443)

# Step 1: Create graph
try:
    result = conn.gsql('CREATE GRAPH HHGOA_Fraud_Graph()')
    print(f"CREATE GRAPH: {result}")
except Exception as e:
    print(f"CREATE GRAPH: {type(e).__name__}: {str(e)[:200]}")

# Step 2: Use graph
try:
    result = conn.gsql('USE GRAPH HHGOA_Fraud_Graph')
    print(f"USE GRAPH: {result}")
except Exception as e:
    print(f"USE GRAPH: {type(e).__name__}: {str(e)[:200]}")

# Step 3: Parse schema into individual statements (with {} depth tracking)
with open('tigergraph/schema/schema.gsql') as f:
    content = f.read()

# Remove single-line comments
content = re.sub(r'//[^\n]*', '', content)

# Tokenize and parse statements respecting (), {}, and [] brackets
statements = []
depth_paren = 0  # ( )
depth_brace = 0  # { }
depth_bracket = 0  # [ ]
current = []

for char in content:
    if char == '(':
        depth_paren += 1
    elif char == ')':
        depth_paren -= 1
    elif char == '{':
        depth_brace += 1
    elif char == '}':
        depth_brace -= 1
    elif char == '[':
        depth_bracket += 1
    elif char == ']':
        depth_bracket -= 1

    if char == ';' and depth_paren == 0 and depth_brace == 0 and depth_bracket == 0:
        stmt = ''.join(current).strip()
        if stmt:
            statements.append(stmt)
        current = []
    else:
        current.append(char)

# Add remaining
last = ''.join(current).strip()
if last:
    statements.append(last)

print(f"\nFound {len(statements)} statements:")
for i, s in enumerate(statements):
    preview = s[:80].replace('\n', ' ')
    print(f"  {i+1}: {preview}...")

# Step 4: Deploy each statement
print("\n--- Deployment ---")
results = []
for i, stmt in enumerate(statements):
    # Skip DROP/CREATE/USE GRAPH (graph already created and in use)
    if stmt.startswith('DROP GRAPH') or stmt.startswith('CREATE GRAPH') or stmt.startswith('USE GRAPH'):
        results.append((i+1, "SKIP", "SKIPPED", ""))
        continue
    try:
        result = conn.gsql(stmt)
        results.append((i+1, "PASS", str(result)[:150], stmt[:60]))
        print(f"  [{i+1}/{len(statements)}] PASS: {stmt[:60]}")
    except Exception as e:
        err_msg = f"{type(e).__name__}: {str(e)[:200]}"
        results.append((i+1, "FAIL", err_msg, stmt[:60]))
        print(f"  [{i+1}/{len(statements)}] FAIL: {stmt[:60]} -> {err_msg}")

# Summary
print("\n--- Results ---")
passed = sum(1 for r in results if r[1] == "PASS")
failed = sum(1 for r in results if r[1] == "FAIL")
skipped = sum(1 for r in results if r[1] == "SKIP")
print(f"PASS: {passed}, FAIL: {failed}, SKIP: {skipped}")
for num, status, msg, stmt in results:
    if status == "FAIL":
        print(f"  {num}. {stmt}: {msg}")
