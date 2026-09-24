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

# Check GDBMS_ALGO packages
tests = [
    "SHOW PACKAGE GDBMS_ALGO.path",
    "SHOW PACKAGE GDBMS_ALGO.bfs",
    "SHOW PACKAGE GDBMS_ALGO.dijkstra",
    "SHOW PACKAGE GDBMS_ALGO.shortestPath",
    "SHOW PACKAGE GDBMS_ALGO.floyd_warshall",
    "SHOW PACKAGE GDBMS_ALGO.johnson",
    "INSTALL FUNCTION GDBMS_ALGO.path.*",
    "INSTALL FUNCTION GDBMS_ALGO.bfs.*",
]

for t in tests:
    print("=== " + t + " ===")
    try:
        r = conn.gsql(t)
        print(str(r)[:500])
    except Exception as e:
        print("Error:", type(e).__name__, str(e)[:300])
    print()
