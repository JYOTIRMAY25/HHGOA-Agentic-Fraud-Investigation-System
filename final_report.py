#!/usr/bin/env python3
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

print("=" * 70)
print("HHGOA_Fraud_Graph - Deployment Blocker Report")
print("=" * 70)

# 1. Deployed Transaction definition
print("\n=== DEPLOYED Transaction Definition ===")
try:
    r = conn.gsql('SHOW VERTEX Transaction')
    print(str(r).strip())
except Exception as e:
    print("Error:", e)

# 2. schema.gsql Transaction definition
print("\n=== SCHEMA.GSQL Transaction Definition ===")
with open('tigergraph/schema/schema.gsql') as f:
    content = f.read()
for line in content.split('\n'):
    if 'CREATE VERTEX Transaction' in line or 'Transaction' in line:
        print(line)
# Better: extract the Transaction block
in_txn = False
for line in content.split('\n'):
    if 'CREATE VERTEX Transaction' in line:
        in_txn = True
    if in_txn:
        print(line)
        if line.strip() == ');':
            break

# 3. Mismatch
print("\n=== MISMATCH ===")
print("Deployed: Transaction(PRIMARY_ID id STRING) - no other attributes")
print("schema.gsql: Transaction(PRIMARY_ID transaction_id STRING, ts DATETIME, amount FLOAT, channel STRING, product_cd STRING, risk_score FLOAT, dist1 FLOAT, dist2 FLOAT, is_flagged BOOL DEFAULT false)")
print("Diff: PRIMARY_ID differs (id vs transaction_id); schema.gsql has 8 additional attributes not in deployed schema")

# Also check BillingRegion and FraudCase
print("\n--- Additional Mismatches ---")
for vname in ['BillingRegion', 'FraudCase']:
    in_v = False
    file_def = []
    for line in content.split('\n'):
        if 'CREATE VERTEX ' + vname in line:
            in_v = True
        if in_v:
            file_def.append(line.strip())
            if line.strip() == ');':
                break
    
    print(f"\n{vname}:")
    print(f"  schema.gsql: {' '.join(file_def)}")

# 4. Final shortestPath GSQL
print("\n=== FINAL shortestPath GSQL (from schema.gsql) ===")
for line in content.split('\n'):
    if 'CREATE OR REPLACE QUERY shortestPath' in line or 'shortestPath' in line.lower() and 'CREATE' not in line:
        print(line)
# Extract the full query
in_q = False
for line in content.split('\n'):
    if 'CREATE OR REPLACE QUERY shortestPath' in line:
        in_q = True
    if in_q:
        print(line)
        if line.strip() == '}':
            break

# 5. Deploy and get compile result
print("\n=== DEPLOYING QUERY ===")
# Drop existing
try:
    conn.gsql('DROP QUERY shortestPath')
except:
    pass

# Read query from schema.gsql
lines = content.split('\n')
query_lines = []
in_q = False
brace_d = 0
for line in lines:
    if 'CREATE OR REPLACE QUERY shortestPath' in line:
        in_q = True
    if in_q:
        query_lines.append(line)
        brace_d += line.count('{') - line.count('}')
        if brace_d == 0 and len(query_lines) > 1:
            break
query = '\n'.join(query_lines)
full_query = "USE GRAPH HHGOA_Fraud_Graph\n" + query

try:
    r = conn.gsql(full_query)
    print("Deploy result:")
    print(str(r)[:500])
except Exception as e:
    print("Deploy error:", type(e).__name__, str(e)[:500])

# 6. Check install status
print("\n=== INSTALL STATUS ===")
try:
    r = conn.getQueryInfo("shortestPath")
    res = r.get('results', [])
    if res:
        status = res[0].get('status', 'UNKNOWN')
        installed = res[0].get('installed', False)
        error = res[0].get('error', True)
        print("Status:", status)
        print("Installed:", installed)
        print("Has errors:", error)
        if status == "COMPILED" and not error:
            print("INSTALL: SUCCESS")
        else:
            print("INSTALL: NOT INSTALLED (compilation failed)")
    else:
        print("Query not found")
except Exception as e:
    print("Status check error:", type(e).__name__, str(e)[:200])

print("\n" + "=" * 70)
print("END OF REPORT")
print("=" * 70)
