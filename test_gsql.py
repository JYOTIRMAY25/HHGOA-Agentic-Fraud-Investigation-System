#!/usr/bin/env python3
"""Debug conn.gsql() return behavior."""
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

conn.gsql("DROP GRAPH HHGOA_Fraud_Graph CASCADE")
time.sleep(5)
conn.gsql("CREATE GRAPH HHGOA_Fraud_Graph()")
time.sleep(5)
conn.gsql("USE GRAPH HHGOA_Fraud_Graph")
time.sleep(3)

# Test simple CREATE VERTEX
print("=== Simple CREATE VERTEX ===")
r = conn.gsql("CREATE VERTEX TestA ( PRIMARY_ID id STRING );")
print(f"  Type: {type(r)}")
print(f"  Repr: {repr(r)[:300]}")
print(f"  Str: {str(r)[:300]}")
time.sleep(1)

# Test SHOW VERTEX
print("\n=== SHOW VERTEX ===")
r = conn.gsql("SHOW VERTEX *")
print(f"  Type: {type(r)}")
print(f"  Str: {str(r)[:300]}")

# Test a query
print("\n=== SELECT count ===")
try:
    r = conn.gsql("SELECT count(*) FROM TestA")
    print(f"  Type: {type(r)}")
    print(f"  Str: {str(r)[:300]}")
except Exception as e:
    print(f"  Error: {type(e).__name__}: {str(e)[:200]}")

time.sleep(1)

# Check if TestA was actually created
print("\n=== Check TestA exists ===")
try:
    r = conn.getVertexType("TestA")
    print(f"  getVertexType: {r}")
except Exception as e:
    print(f"  Error: {type(e).__name__}: {str(e)[:200]}")

# Try using USE GRAPH explicitly in each call
print("\n=== Create with explicit USE GRAPH ===")
r = conn.gsql("USE GRAPH HHGOA_Fraud_Graph; CREATE VERTEX TestB ( PRIMARY_ID id STRING );")
print(f"  Type: {type(r)}")
print(f"  Str: {str(r)[:300]}")
time.sleep(2)

try:
    r = conn.getVertexType("TestB")
    print(f"  getVertexType TestB: {r}")
except Exception as e:
    print(f"  Error: {type(e).__name__}: {str(e)[:200]}")
