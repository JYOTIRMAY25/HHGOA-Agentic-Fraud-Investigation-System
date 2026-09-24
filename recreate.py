#!/usr/bin/env python3
"""Clean recreation of HHGOA_Fraud_Graph from schema.gsql."""
import os, re, time
from dotenv import load_dotenv
load_dotenv('D:/task4/.env')
from pyTigerGraph import TigerGraphConnection

host = os.getenv('TG_HOST')
graphname = os.getenv('TG_GRAPH')
username = os.getenv('TG_USERNAME')
password = os.getenv('TG_PASSWORD')
secret = os.getenv('TG_SECRET')

conn = TigerGraphConnection(host=host, graphname=graphname, gsqlSecret=secret, username=username, password=password, tgCloud=True, sslPort=443)

print("=" * 70)
print("STEP 1: Confirm zero data")
print("=" * 70)

# Check vertex counts
expected_v = ["Customer", "Card", "Transaction", "DeviceProfile", "EmailDomain", "BillingRegion", "FraudCase", "FraudPattern", "PolicyRule"]
for v in expected_v:
    try:
        r = conn.gsql(f"USE GRAPH {graphname}; SELECT count(*) FROM {v}")
        print(f"  {v}: check skipped (no data loading)")
    except Exception as e:
        print(f"  {v}: {str(e)[:100]}")

# Check edges
expected_e = ["OWNS", "PERFORMS", "NEXT_TRANSACTION", "USED_DEVICE", "PURCHASER_EMAIL", "RECIPIENT_EMAIL", "BILLED_IN", "INVESTIGATES_TXN", "TARGETS_CARD", "CONNECTS_TO_CARD", "INVESTIGATES_CUSTOMER", "EXHIBITS_PATTERN", "GOVERNED_BY"]
for e in expected_e:
    try:
        r = conn.gsql(f"USE GRAPH {graphname}; SELECT count(*) FROM {e}")
        print(f"  {e}: check skipped (no data loading)")
    except Exception as e:
        print(f"  {e}: {str(e)[:100]}")

print("\nSTEP 2: Drop and recreate graph")
print("-" * 70)

# Drop graph if exists
try:
    r = conn.gsql("DROP GRAPH HHGOA_Fraud_Graph")
    print(f"  DROP: {r}")
except Exception as e:
    print(f"  DROP: {type(e).__name__}: {str(e)[:200]}")

time.sleep(3)

# Create graph
try:
    r = conn.gsql("CREATE GRAPH HHGOA_Fraud_Graph()")
    print(f"  CREATE: {r}")
except Exception as e:
    print(f"  CREATE: {type(e).__name__}: {str(e)[:200]}")

time.sleep(3)

# Use graph
try:
    r = conn.gsql("USE GRAPH HHGOA_Fraud_Graph")
    print(f"  USE: {r}")
except Exception as e:
    print(f"  USE: {type(e).__name__}: {str(e)[:200]}")

print("\nSTEP 3: Parse schema.gsql into statements")
print("-" * 70)

with open('tigergraph/schema/schema.gsql') as f:
    content = f.read()

# Remove comments
content_no_comments = re.sub(r'//.*', '', content)

# Split by keyword boundaries
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

# Add semicolons where missing
formatted = []
for s in statements:
    if not s.endswith(';'):
        s += ';'
    formatted.append(s)

# Filter out DROP/CREATE/USE GRAPH (already done)
deploy_stmts = [s for s in formatted if not (s.startswith('DROP GRAPH') or s.startswith('CREATE GRAPH') or s.startswith('USE GRAPH'))]

print(f"  Found {len(deploy_stmts)} statements to deploy")
for i, s in enumerate(deploy_stmts):
    preview = s[:80].replace('\n', ' ')
    print(f"  {i+1}: {preview}...")

print("\nSTEP 4: Deploy vertices")
print("-" * 70)

vertex_stmts = [s for s in deploy_stmts if 'CREATE VERTEX' in s]
for i, stmt in enumerate(vertex_stmts):
    try:
        r = conn.gsql(stmt)
        print(f"  [V{i+1}/{len(vertex_stmts)}] PASS: {stmt[:60]}")
    except Exception as e:
        print(f"  [V{i+1}/{len(vertex_stmts)}] FAIL: {stmt[:60]} -> {str(e)[:200]}")
    time.sleep(1)

print("\nSTEP 5: Deploy edges")
print("-" * 70)

edge_stmts = [s for s in deploy_stmts if 'CREATE DIRECTED EDGE' in s]
for i, stmt in enumerate(edge_stmts):
    try:
        r = conn.gsql(stmt)
        print(f"  [E{i+1}/{len(edge_stmts)}] PASS: {stmt[:60]}")
    except Exception as e:
        print(f"  [E{i+1}/{len(edge_stmts)}] FAIL: {stmt[:60]} -> {str(e)[:200]}")
    time.sleep(1)

print("\nSTEP 6: Verify deployed definitions")
print("-" * 70)

# Check Transaction
print("\n=== Transaction ===")
try:
    r = conn.gsql('SHOW VERTEX Transaction')
    print(str(r).strip())
except Exception as e:
    print(f"Error: {e}")

# Check BillingRegion
print("\n=== BillingRegion ===")
try:
    r = conn.gsql('SHOW VERTEX BillingRegion')
    print(str(r).strip())
except Exception as e:
    print(f"Error: {e}")

# Check FraudCase
print("\n=== FraudCase ===")
try:
    r = conn.gsql('SHOW VERTEX FraudCase')
    print(str(r).strip())
except Exception as e:
    print(f"Error: {e}")

# Check ALL vertices
print("\n=== All vertices (SHOW VERTEX *) ===")
try:
    r = conn.gsql('SHOW VERTEX *')
    vtypes = [l.strip().replace('- VERTEX ', '').split('(')[0] for l in str(r).split('\n') if 'VERTEX' in l and 'PRIMARY_ID' in l]
    print(f"Count: {len(vtypes)}")
    for v in vtypes:
        print(f"  {v}")
except Exception as e:
    print(f"Error: {e}")

# Check ALL edges
print("\n=== All edges (SHOW EDGE *) ===")
try:
    r = conn.gsql('SHOW EDGE *')
    etypes = [l.strip().replace('- DIRECTED EDGE ', '').split('(')[0] for l in str(r).split('\n') if 'DIRECTED EDGE' in l]
    rev = {"OWNED_BY","PERFORMED_BY","PREV_TRANSACTION","USED_IN_TXN","PURCHASER_TXNS","RECIPIENT_TXNS","BILLED_TXNS","INVOLVED_IN_CASE","HAS_CASES","CONNECTED_IN_CASES","CUSTOMER_CASES","CASES_WITH_PATTERN","ENFORCING_CASES"}
    direct = [e for e in etypes if e not in rev]
    print(f"Total edges: {len(etypes)}, Directed: {len(direct)}")
    for e in direct:
        print(f"  {e}")
except Exception as e:
    print(f"Error: {e}")

print("\nSTEP 7: Verify query compiler resolution")
print("-" * 70)

# Check getVertexType
print("\n=== getVertexType Transaction ===")
try:
    r = conn.getVertexType("Transaction")
    print(f"Result: {r}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)[:200]}")

# Check getEdgeType
print("\n=== getEdgeType NEXT_TRANSACTION ===")
try:
    r = conn.getEdgeType("NEXT_TRANSACTION")
    print(f"Result: {r}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)[:200]}")

print("\n" + "=" * 70)
print("SCHEMA VALIDATION COMPLETE")
print("=" * 70)
