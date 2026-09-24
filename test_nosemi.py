#!/usr/bin/env python3
"""Test conn.gsql without semicolons."""
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

# Drop and create fresh
conn.gsql("DROP GRAPH HHGOA_Fraud_Graph CASCADE")
time.sleep(5)
conn.gsql("CREATE GRAPH HHGOA_Fraud_Graph()")
time.sleep(5)

# Test: USE GRAPH first, then CREATE VERTEX without semicolon
print("=== Test 1: USE GRAPH then CREATE VERTEX (no semicolon) ===")
r = conn.gsql("USE GRAPH HHGOA_Fraud_Graph")
print(f"  USE: {str(r)[:100]}")
time.sleep(2)

r = conn.gsql("CREATE VERTEX TestA ( PRIMARY_ID id STRING )")
print(f"  CREATE: {str(r)[:200]}")
time.sleep(2)

r = conn.gsql("SHOW VERTEX TestA")
print(f"  SHOW: {str(r)[:200]}")

# Check via getVertexType
try:
    r = conn.getVertexType("TestA")
    print(f"  getVertexType: {r}")
except Exception as e:
    print(f"  getVertexType Error: {e}")

# Test 2: Deploy full Transaction without DEFAULT
print("\n=== Test 2: Transaction without DEFAULT ===")
r = conn.gsql("USE GRAPH HHGOA_Fraud_Graph")
time.sleep(1)
r = conn.gsql("CREATE VERTEX Transaction ( PRIMARY_ID transaction_id STRING, ts DATETIME, amount FLOAT, channel STRING, product_cd STRING, risk_score FLOAT, dist1 FLOAT, dist2 FLOAT, is_flagged BOOL )")
print(f"  CREATE: {str(r)[:200]}")
time.sleep(2)

r = conn.gsql("SHOW VERTEX Transaction")
print(f"  SHOW: {str(r)[:300]}")
