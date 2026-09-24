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

# Try listing packages
tests = [
    "SHOW PACKAGE *",
    "SHOW PACKAGE gsql.*",
    "SHOW PACKAGE GDBMS_ALGO.*",
    "INSTALL FUNCTION gsql.*",
    "INSTALL FUNCTION GDBMS_ALGO.*",
]

for t in tests:
    print("=== " + t + " ===")
    try:
        r = conn.gsql(t)
        print("Result:", str(r)[:500])
    except Exception as e:
        print("Error:", type(e).__name__, str(e)[:200])
    print()

# Try install with correct syntax
print("=== Try install from GDBMS_ALGO.path ===")
tests2 = [
    "INSTALL FUNCTION GDBMS_ALGO.path.*",
    "INSTALL FUNCTION GDBMS_ALGO.**",
]
for t in tests2:
    print("--- " + t + " ---")
    try:
        r = conn.gsql(t)
        print("Result:", str(r)[:300])
    except Exception as e:
        print("Error:", type(e).__name__, str(e)[:200])
