#!/usr/bin/env python3
"""Clean recreation of HHGOA_Fraud_Graph."""
import os, time
from dotenv import load_dotenv
load_dotenv('D:/task4/.env')
from pyTigerGraph import TigerGraphConnection

host = os.getenv('TG_HOST')
graphname = os.getenv('TG_GRAPH')
username = os.getenv('TG_USERNAME')
password = os.getenv('TG_PASSWORD')
secret = os.getenv('TG_SECRET')

conn = TigerGraphConnection(host=host, graphname=graphname, gsqlSecret=secret, username=username, password=password, tgCloud=True, sslPort=443)

print("STEP 1: Create fresh graph")
try:
    r = conn.gsql("CREATE GRAPH HHGOA_Fraud_Graph()")
    print(f"  {r}")
except Exception as e:
    print(f"  Error: {type(e).__name__}: {str(e)[:300]}")

time.sleep(5)

try:
    r = conn.gsql("USE GRAPH HHGOA_Fraud_Graph")
    print(f"  {r}")
except Exception as e:
    print(f"  Error: {type(e).__name__}: {str(e)[:300]}")

time.sleep(2)

print("\nSTEP 2: Parse and deploy schema")
import re

with open('tigergraph/schema/schema.gsql') as f:
    content = f.read()

content_no_comments = re.sub(r'//.*', '', content)

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

# Filter out DROP/CREATE/USE GRAPH (graph already created)
deploy_stmts = [s for s in statements if not (s.startswith('DROP GRAPH') or s.startswith('CREATE GRAPH') or s.startswith('USE GRAPH'))]

# Add semicolons
formatted = []
for s in deploy_stmts:
    if not s.endswith(';'):
        s += ';'
    formatted.append(s)

print(f"  Deploying {len(formatted)} statements...")

print("\nSTEP 3: Deploy vertices")
vertex_stmts = [s for s in formatted if 'CREATE VERTEX' in s]
for i, stmt in enumerate(vertex_stmts):
    time.sleep(2)
    try:
        r = conn.gsql(stmt)
        print(f"  [V{i+1}/{len(vertex_stmts)}] PASS")
    except Exception as e:
        print(f"  [V{i+1}/{len(vertex_stmts)}] FAIL: {str(e)[:200]}")

print("\nSTEP 4: Deploy edges")
edge_stmts = [s for s in formatted if 'CREATE DIRECTED EDGE' in s]
for i, stmt in enumerate(edge_stmts):
    time.sleep(2)
    try:
        r = conn.gsql(stmt)
        print(f"  [E{i+1}/{len(edge_stmts)}] PASS")
    except Exception as e:
        print(f"  [E{i+1}/{len(edge_stmts)}] FAIL: {str(e)[:200]}")

print("\nSTEP 5: Verify definitions")
print("\n=== Transaction ===")
try:
    r = conn.gsql('SHOW VERTEX Transaction')
    print(str(r).strip())
except Exception as e:
    print(f"Error: {e}")

print("\n=== BillingRegion ===")
try:
    r = conn.gsql('SHOW VERTEX BillingRegion')
    print(str(r).strip())
except Exception as e:
    print(f"Error: {e}")

print("\n=== FraudCase ===")
try:
    r = conn.gsql('SHOW VERTEX FraudCase')
    print(str(r).strip())
except Exception as e:
    print(f"Error: {e}")

print("\n=== All vertices ===")
try:
    r = conn.gsql('SHOW VERTEX *')
    vtypes = [l.strip().replace('- VERTEX ', '').split('(')[0] for l in str(r).split('\n') if 'VERTEX' in l and 'PRIMARY_ID' in l]
    print(f"Count: {len(vtypes)}")
    for v in vtypes:
        print(f"  {v}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== All directed edges ===")
try:
    r = conn.gsql('SHOW EDGE *')
    all_e = [l.strip().replace('- DIRECTED EDGE ', '').split('(')[0] for l in str(r).split('\n') if 'DIRECTED EDGE' in l]
    rev = {"OWNED_BY","PERFORMED_BY","PREV_TRANSACTION","USED_IN_TXN","PURCHASER_TXNS","RECIPIENT_TXNS","BILLED_TXNS","INVOLVED_IN_CASE","HAS_CASES","CONNECTED_IN_CASES","CUSTOMER_CASES","CASES_WITH_PATTERN","ENFORCING_CASES"}
    direct = [e for e in all_e if e not in rev]
    print(f"Directed count: {len(direct)}")
    for e in direct:
        print(f"  {e}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== Query compiler: getVertexType Transaction ===")
try:
    r = conn.getVertexType("Transaction")
    print(f"Result: {r}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)[:200]}")

print("\n=== Query compiler: getEdgeType NEXT_TRANSACTION ===")
try:
    r = conn.getEdgeType("NEXT_TRANSACTION")
    print(f"Result: {r}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)[:200]}")

print("\n" + "=" * 70)
print("SCHEMA VALIDATION COMPLETE - STOP")
print("=" * 70)
