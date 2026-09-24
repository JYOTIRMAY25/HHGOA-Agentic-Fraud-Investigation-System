#!/usr/bin/env python3
"""Test various boolean/default syntaxes."""
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
    ("No DEFAULT", 'CREATE VERTEX Test1 ( PRIMARY_ID id STRING, flag BOOL );'),
    ("DEFAULT = false", 'CREATE VERTEX Test2 ( PRIMARY_ID id STRING, flag BOOL DEFAULT = false );'),
    ("DEFAULT = FALSE", 'CREATE VERTEX Test3 ( PRIMARY_ID id STRING, flag BOOL DEFAULT = FALSE );'),
    ("DEFAULT (false)", 'CREATE VERTEX Test4 ( PRIMARY_ID id STRING, flag BOOL DEFAULT (false) );'),
    ("DEFAULT (FALSE)", 'CREATE VERTEX Test5 ( PRIMARY_ID id STRING, flag BOOL DEFAULT (FALSE) );'),
    ("DEFAULT 'false'", 'CREATE VERTEX Test6 ( PRIMARY_ID id STRING, flag BOOL DEFAULT \'false\' );'),
    ("DEFAULT 'FALSE'", 'CREATE VERTEX Test7 ( PRIMARY_ID id STRING, flag BOOL DEFAULT \'FALSE\' );'),
    ("Default false", 'CREATE VERTEX Test8 ( PRIMARY_ID id STRING, flag BOOL Default false );'),
    ("No default, check BOOL", 'CREATE VERTEX Test9 ( PRIMARY_ID id STRING, flag INT DEFAULT 0 );'),
]

for name, sql in tests:
    r = conn.gsql(sql)
    result = str(r).strip()
    success = "PASS" if "Error" not in result and "Semantic" not in result and "Encountered" not in result else "FAIL"
    print(f"{success}: {name}: {result[:150]}")
    time.sleep(1)

print("\n=== SHOW VERTEX Test9 ===")
r = conn.gsql("SHOW VERTEX Test9")
print(str(r).strip())
