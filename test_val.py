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

# Try validateGraphSchema
print("=== validateGraphSchema ===")
try:
    r = conn.validateGraphSchema()
    print("Result:", str(r)[:300])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])

# Try getVertexType
print("\n=== getVertexType Transaction ===")
try:
    r = conn.getVertexType("Transaction")
    print("Result:", str(r)[:500])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])

# Try getEdgeType
print("\n=== getEdgeType NEXT_TRANSACTION ===")
try:
    r = conn.getEdgeType("NEXT_TRANSACTION")
    print("Result:", str(r)[:300])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])

# Try using all_path template query
print("\n=== Try all_path ===")
q = ("USE GRAPH " + GN + nl +
     "CREATE OR REPLACE Q1(STRING sid, STRING eid) {" +
     "S = to_vertex(sid, \"Transaction\");" +
     "E = to_vertex(eid, \"Transaction\");" +
     "P = all_path(S, E, 10, true, \"\");" +
     "PRINT P;" +
     "}")
try:
    r = conn.gsql(q)
    print("Result:", str(r)[:300])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])

# Try bfs
print("\n=== Try bfs ===")
q2 = ("USE GRAPH " + GN + nl +
      "CREATE OR REPLACE Q2(STRING sid, STRING eid) {" +
      "S = to_vertex(sid, \"Transaction\");" +
      "E = to_vertex(eid, \"Transaction\");" +
      "P = bfs({\"Transaction\"}, {\"NEXT_TRANSACTION\"}, 10, S, true, \"result\", \"\", false);" +
      "PRINT P;" +
      "}")
try:
    r = conn.gsql(q2)
    print("Result:", str(r)[:300])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])
