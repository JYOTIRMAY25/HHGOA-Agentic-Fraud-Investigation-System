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

# Try all_path with correct QUERY syntax
q = ("USE GRAPH " + GN + nl +
     "CREATE OR REPLACE QUERY sp_path(STRING sid, STRING eid) {" +
     "S = to_vertex(sid, \"Transaction\");" +
     "E = to_vertex(eid, \"Transaction\");" +
     "P = all_path(S, E, 10, true, \"\");" +
     "PRINT P;" +
     "}")
print("=== all_path ===")
try:
    r = conn.gsql(q)
    print("Result:", str(r)[:500])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:500])

# Try with vertex type in to_vertex
q2 = ("USE GRAPH " + GN + nl +
      "CREATE OR REPLACE QUERY sp_path2(STRING sid, STRING eid) {" +
      "S = to_vertex(sid, Transaction);" +
      "E = to_vertex(eid, Transaction);" +
      "P = all_path(S, E, 10, true, \"\");" +
      "PRINT P;" +
      "}")
print("\n=== all_path (no quotes) ===")
try:
    r = conn.gsql(q2)
    print("Result:", str(r)[:500])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:500])

# Try simple traversal
q3 = ("USE GRAPH " + GN + nl +
      "CREATE OR REPLACE QUERY sp_simple(STRING sid, STRING eid) {" +
      "S = to_vertex(sid, \"Transaction\");" +
      "P = SELECT t FROM S:s -(NEXT_TRANSACTION:e)-> t WHERE t.id == eid ACCUM @@path += t.id; PRINT S, P;" +
      "}")
print("\n=== simple traversal ===")
try:
    r = conn.gsql(q3)
    print("Result:", str(r)[:500])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:500])

# Try with ACCUM outside SELECT
q4 = ("USE GRAPH " + GN + nl +
      "CREATE OR REPLACE QUERY sp_acc(STRING sid, STRING eid) {" +
      "ListAccum<STRING> @@path;" +
      "S = to_vertex(sid, \"Transaction\");" +
      "T = to_vertex(eid, \"Transaction\);" +
      "P = S -(NEXT_TRANSACTION:e)-> T;" +
      "@@path += T.id;" +
      "PRINT P, @@path;" +
      "}")
print("\n=== acc traversal ===")
try:
    r = conn.gsql(q4)
    print("Result:", str(r)[:500])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:500])
