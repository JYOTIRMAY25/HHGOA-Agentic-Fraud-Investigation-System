#!/usr/bin/env python3
"""Test proper DDL deployment methods."""
import os, time, json, urllib.request, urllib.parse
from dotenv import load_dotenv
load_dotenv('D:/task4/.env')
from pyTigerGraph import TigerGraphConnection

host = os.getenv('TG_HOST')
graphname = os.getenv('TG_GRAPH')
username = os.getenv('TG_USERNAME')
password = os.getenv('TG_PASSWORD')
secret = os.getenv('TG_SECRET')

conn = TigerGraphConnection(host=host, graphname=graphname, gsqlSecret=secret, username=username, password=password, tgCloud=True, sslPort=443)

# First, let me try the raw REST API for DDL
# TigerGraph Cloud REST API endpoint for GSQL
def run_gsql(gsql_cmd, use_graph=None):
    """Run GSQL via REST API."""
    url = f"{host}/gsql-server/gsql"
    params = {'gsql': gsql_cmd}
    if use_graph:
        params['graph'] = use_graph
    data = urllib.parse.urlencode(params).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    if secret:
        req.add_header('authorization', f'tg_secret {secret}')
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return f"HTTP Error {e.code}: {e.read().decode('utf-8')[:500]}"
    except Exception as e:
        return f"Error: {type(e).__name__}: {str(e)[:300]}"

# Test with USE GRAPH first
print("=== Test 1: USE GRAPH + CREATE VERTEX via REST ===")
r = run_gsql("USE GRAPH HHGOA_Fraud_Graph")
print(f"  USE: {r[:200]}")
time.sleep(2)
r = run_gsql("CREATE VERTEX TestA ( PRIMARY_ID id STRING )")
print(f"  CREATE: {r[:200]}")
time.sleep(2)
r = run_gsql("SHOW VERTEX TestA")
print(f"  SHOW: {r[:200]}")
time.sleep(2)

print("\n=== Test 2: No semicolon, no USE GRAPH ===")
r = run_gsql("CREATE VERTEX TestB ( PRIMARY_ID id STRING )", graphname)
print(f"  CREATE: {r[:200]}")
time.sleep(2)
r = run_gsql("SHOW VERTEX TestB", graphname)
print(f"  SHOW: {r[:200]}")

print("\n=== Test 3: Try with gsql parameter as JSON ===")
# Maybe the API expects different parameter format
url = f"{host}/gsql-server/gsql"
data = json.dumps({'gsql': 'CREATE VERTEX TestC ( PRIMARY_ID id STRING )', 'graph': graphname}).encode('utf-8')
req = urllib.request.Request(url, data=data, method='POST')
req.add_header('Content-Type', 'application/json')
if secret:
    req.add_header('authorization', f'tg_secret {secret}')
try:
    with urllib.request.urlopen(req, timeout=30) as response:
        r = response.read().decode('utf-8')
        print(f"  JSON CREATE: {r[:200]}")
except urllib.error.HTTPError as e:
    print(f"  JSON CREATE Error: HTTP {e.code}: {e.read().decode('utf-8')[:200]}")
