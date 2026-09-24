#!/usr/bin/env python3
"""Test DEFAULT with no semicolon, plus find correct boolean syntax."""
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

conn.gsql("DROP GRAPH HHGOA_Fraud_Graph CASCADE")
time.sleep(5)
conn.gsql("CREATE GRAPH HHGOA_Fraud_Graph()")
time.sleep(5)
conn.gsql("USE GRAPH HHGOA_Fraud_Graph")
time.sleep(3)

tests = [
    ("BOOL no DEFAULT", "CREATE VERTEX T1 ( PRIMARY_ID id STRING, flag BOOL )"),
    ("BOOL DEFAULT false", "CREATE VERTEX T2 ( PRIMARY_ID id STRING, flag BOOL DEFAULT false )"),
    ("BOOL DEFAULT FALSE", "CREATE VERTEX T3 ( PRIMARY_ID id STRING, flag BOOL DEFAULT FALSE )"),
    ("BOOL DEFAULT = false", "CREATE VERTEX T4 ( PRIMARY_ID id STRING, flag BOOL DEFAULT = false )"),
    ("BOOL DEFAULT (false)", "CREATE VERTEX T5 ( PRIMARY_ID id STRING, flag BOOL DEFAULT (false) )"),
]

for name, sql in tests:
    r = conn.gsql(sql)
    result = str(r).strip()
    print(f"{name}: {result[:200]}")
    time.sleep(2)

print("\n=== SHOW VERTEX T1 ===")
r = conn.gsql("SHOW VERTEX T1")
print(str(r).strip()[:200])
