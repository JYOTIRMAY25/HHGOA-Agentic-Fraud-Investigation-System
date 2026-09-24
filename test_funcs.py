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

GN = graphname
nl = chr(10)

funcs = ["to_vertex", "to_vertex_set", "getVertex", "get_vertex", "resolveVertex", "resolve_vertex", "findVertex", "find_vertex", "vertexById", "v", "vertex"]

for f in funcs:
    q = "USE GRAPH " + GN + nl + "CREATE OR REPLACE QUERY t(STRING tid) { S = " + f + "(tid, \"Customer\"); PRINT S; }"
    print("=== " + f + " ===")
    try:
        r = conn.gsql(q)
        print("Result:", str(r)[:200])
    except Exception as e:
        print("Error:", type(e).__name__, str(e)[:200])
    print()
