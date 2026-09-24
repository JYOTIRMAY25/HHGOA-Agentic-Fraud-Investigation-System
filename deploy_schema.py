#!/usr/bin/env python3
"""Deploy schema to TigerGraph step by step."""
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

# Pre-config: drop and create graph
try: conn.gsql('DROP GRAPH HHGOA_Fraud_Graph')
except: pass
try: conn.gsql('CREATE GRAPH HHGOA_Fraud_Graph()')
except Exception as e: print('CREATE GRAPH:', e)
try: conn.gsql('USE GRAPH HHGOA_Fraud_Graph')
except Exception as e: print('USE GRAPH:', e)

# Read and parse schema
with open('tigergraph/schema/schema.gsql') as f:
    content = f.read()

# Remove single-line comments
content = re.sub(r'//[^\n]*', '', content)

# Replace newlines with spaces for easier parsing, but keep structure
content = re.sub(r'\s+', ' ', content).strip()

# Split by semicolons at top level (depth 0)
statements = []
depth = 0
current = []
for char in content:
    if char == '(':
        depth += 1
    elif char == ')':
        depth -= 1
    if char == ';' and depth == 0:
        stmt = ''.join(current).strip()
        if stmt:
            statements.append(stmt)
        current = []
    else:
        current.append(char)

# Skip DROP GRAPH and CREATE GRAPH and USE GRAPH (already done)
deploy_stmts = []
for s in statements:
    if s.startswith('DROP GRAPH') or s.startswith('CREATE GRAPH') or s.startswith('USE GRAPH'):
        continue
    deploy_stmts.append(s)

print(f"Deploying {len(deploy_stmts)} statements...")

results = []
for i, stmt in enumerate(deploy_stmts):
    try:
        result = conn.gsql(stmt)
        results.append((i+1, stmt[:60], "PASS", str(result)[:100]))
        print(f"  [{i+1}/{len(deploy_stmts)}] PASS: {stmt[:60]}")
    except Exception as e:
        err_msg = f"{type(e).__name__}: {str(e)[:200]}"
        results.append((i+1, stmt[:60], "FAIL", err_msg))
        print(f"  [{i+1}/{len(deploy_stmts)}] FAIL: {stmt[:60]} -> {err_msg}")

# Summary
print("\n--- Deployment Summary ---")
passed = sum(1 for r in results if r[2] == "PASS")
failed = sum(1 for r in results if r[2] == "FAIL")
print(f"Passed: {passed}, Failed: {failed}")
for num, name, status, msg in results:
    if status == "FAIL":
        print(f"  {num}. {name}: {msg}")