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

nl = chr(10)

# Test 1: Simple to_vertex
q1 = "USE GRAPH " + graphname + nl + "CREATE OR REPLACE QUERY tt(STRING tid) { S = to_vertex(tid, \"Transaction\"); PRINT S; }"
print("=== simple to_vertex ===")
try:
    r = conn.gsql(q1)
    print("Result:", str(r)[:300])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])

# Test 2: to_vertex with traversal
q2 = "USE GRAPH " + graphname + nl + "CREATE OR REPLACE QUERY td(STRING sid, STRING eid) { S = to_vertex(sid, \"Transaction\"); E = to_vertex(eid, \"Transaction\"); P = S -(NEXT_TRANSACTION:e)-> E; PRINT P; }"
print("=== direct traversal ===")
try:
    r = conn.gsql(q2)
    print("Result:", str(r)[:300])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])

# Test 3: to_vertex with ACCUM
q3 = "USE GRAPH " + graphname + nl + "CREATE OR REPLACE QUERY ta(STRING sid, STRING eid) { ListAccum<STRING> @@path; S = to_vertex(sid, \"Transaction\"); E = to_vertex(eid, \"Transaction\"); P = S -(NEXT_TRANSACTION:e)-> E; @@path += E.id; PRINT P, @@path; }"
print("=== traversal with accum ===")
try:
    r = conn.gsql(q3)
    print("Result:", str(r)[:300])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])
