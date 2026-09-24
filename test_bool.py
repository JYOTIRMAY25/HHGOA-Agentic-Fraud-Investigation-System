#!/usr/bin/env python3
"""Test boolean literal syntax."""
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

# Drop and recreate
conn.gsql("DROP GRAPH HHGOA_Fraud_Graph CASCADE")
time.sleep(5)
conn.gsql("CREATE GRAPH HHGOA_Fraud_Graph()")
time.sleep(5)
conn.gsql("USE GRAPH HHGOA_Fraud_Graph")
time.sleep(3)

# Test 1: lowercase false - SHOULD FAIL
print("=== Test 1: DEFAULT false (lowercase) ===")
r = conn.gsql("CREATE VERTEX Test1 ( PRIMARY_ID id STRING, flag BOOL DEFAULT false );")
print(f"  Result: {str(r)[:200]}")
time.sleep(1)

# Test 2: uppercase FALSE - SHOULD PASS
print("\n=== Test 2: DEFAULT FALSE (uppercase) ===")
r = conn.gsql("CREATE VERTEX Test2 ( PRIMARY_ID id STRING, flag BOOL DEFAULT FALSE );")
print(f"  Result: {str(r)[:200]}")
time.sleep(1)

# Test 3: lowercase true - SHOULD FAIL
print("\n=== Test 3: DEFAULT true (lowercase) ===")
r = conn.gsql("CREATE VERTEX Test3 ( PRIMARY_ID id STRING, flag BOOL DEFAULT true );")
print(f"  Result: {str(r)[:200]}")
time.sleep(1)

# Test 4: uppercase TRUE - SHOULD PASS
print("\n=== Test 4: DEFAULT TRUE (uppercase) ===")
r = conn.gsql("CREATE VERTEX Test4 ( PRIMARY_ID id STRING, flag BOOL DEFAULT TRUE );")
print(f"  Result: {str(r)[:200]}")
time.sleep(1)

# Verify
print("\n=== SHOW VERTEX Test2 ===")
r = conn.gsql("SHOW VERTEX Test2")
print(str(r).strip())

print("\n=== SHOW VERTEX Test4 ===")
r = conn.gsql("SHOW VERTEX Test4")
print(str(r).strip())
