#!/usr/bin/env python3
"""Debug CREATE VERTEX deployment."""
import os, time, json
from dotenv import load_dotenv
load_dotenv('D:/task4/.env')
from pyTigerGraph import TigerGraphConnection

host = os.getenv('TG_HOST')
graphname = os.getenv('TG_GRAPH')
username = os.getenv('TG_USERNAME')
password = os.getenv('TG_PASSWORD')
secret = os.getenv('TG_SECRET')

conn = TigerGraphConnection(host=host, graphname=graphname, gsqlSecret=secret, username=username, password=password, tgCloud=True, sslPort=443)

# Drop and recreate
print("=== Dropping graph ===")
try:
    r = conn.gsql("DROP GRAPH HHGOA_Fraud_Graph CASCADE")
    print(f"  {r}")
except Exception as e:
    print(f"  Error: {type(e).__name__}: {str(e)[:200]}")

time.sleep(5)

print("\n=== Creating graph ===")
try:
    r = conn.gsql("CREATE GRAPH HHGOA_Fraud_Graph()")
    print(f"  {r}")
except Exception as e:
    print(f"  Error: {type(e).__name__}: {str(e)[:200]}")

time.sleep(5)

print("\n=== USE GRAPH ===")
try:
    r = conn.gsql("USE GRAPH HHGOA_Fraud_Graph")
    print(f"  {r}")
except Exception as e:
    print(f"  Error: {type(e).__name__}: {str(e)[:200]}")

time.sleep(3)

# Deploy Transaction via raw REST API
print("\n=== Deploy Transaction via conn.gsql ===")
txn_sql = 'CREATE VERTEX Transaction ( PRIMARY_ID transaction_id STRING, ts DATETIME, amount FLOAT, channel STRING, product_cd STRING, risk_score FLOAT, dist1 FLOAT, dist2 FLOAT, is_flagged BOOL DEFAULT false );'
print(f"  SQL: {txn_sql[:100]}")
try:
    r = conn.gsql(txn_sql)
    print(f"  Result: {r}")
except Exception as e:
    print(f"  Error: {type(e).__name__}: {str(e)[:300]}")

time.sleep(3)

print("\n=== SHOW VERTEX Transaction ===")
try:
    r = conn.gsql("SHOW VERTEX Transaction")
    print(str(r).strip())
except Exception as e:
    print(f"  Error: {e}")

print("\n=== SHOW VERTEX Transaction EXTENDED ===")
try:
    r = conn.gsql("SHOW VERTEX Transaction EXTENDED")
    print(str(r).strip())
except Exception as e:
    print(f"  Error: {e}")

# Try via executePost
print("\n=== Try via raw REST API ===")
try:
    # Try /gsql-server/gsql endpoint
    import urllib.request, urllib.parse, json
    url = f"{host}/gsql-server/gsql"
    params = urllib.parse.urlencode({
        'gsql': txn_sql,
        'graph': graphname
    })
    data = params.encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    if secret:
        req.add_header('authorization', f'tg_secret {secret}')
    with urllib.request.urlopen(req, timeout=30) as response:
        result = response.read().decode('utf-8')
        print(f"  REST Result: {result[:500]}")
except Exception as e:
    print(f"  REST Error: {type(e).__name__}: {str(e)[:300]}")

time.sleep(2)

print("\n=== SHOW VERTEX Transaction after REST ===")
try:
    r = conn.gsql("SHOW VERTEX Transaction")
    print(str(r).strip())
except Exception as e:
    print(f"  Error: {e}")
