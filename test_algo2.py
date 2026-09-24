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

# Try to install from gsql-graph-algorithms with different syntaxes
tests = [
    "INSTALL FUNCTION gsql-graph-algorithms.**",
    "INSTALL FUNCTION `gsql-graph-algorithms`.**",
    "INSTALL FUNCTION gsql_graph_algorithms.**",
    "INSTALL FUNCTION gsqlgraphalgorithms.**",
    "SHOW PACKAGE gsql-graph-algorithms.**",
    "SHOW PACKAGE `gsql-graph-algorithms`.**",
    "SHOW PACKAGE gsql_graph_algorithms.**",
    "SHOW PACKAGE gsqlgraphalgorithms.**",
    "SHOW PACKAGE *",
]

for t in tests:
    print("=== " + t[:60] + " ===")
    try:
        r = conn.gsql(t)
        print("Result:", str(r)[:300])
    except Exception as e:
        print("Error:", type(e).__name__, str(e)[:200])
    print()
