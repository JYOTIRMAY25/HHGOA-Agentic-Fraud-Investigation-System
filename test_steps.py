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

# Step 1: Simple to_vertex
q1 = ("USE GRAPH " + GN + nl +
      "CREATE OR REPLACE QUERY shortestPath(STRING start_txn_id, STRING end_txn_id) {" +
      "St = to_vertex(start_txn_id, \"Transaction\");" +
      "Tgt = to_vertex(end_txn_id, \"Transaction\");" +
      "PRINT St, Tgt;" +
      "}")
print("Step 1 - simple to_vertex:")
try:
    r = conn.gsql(q1)
    print("Result:", str(r)[:300])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])

# Drop it first
conn.gsql("DROP QUERY shortestPath")

# Step 2: to_vertex with Traversal using direct syntax
q2 = ("USE GRAPH " + GN + nl +
      "CREATE OR REPLACE QUERY shortestPath(STRING start_txn_id, STRING end_txn_id) {" +
      "St = to_vertex(start_txn_id, \"Transaction\");" +
      "Tgt = to_vertex(end_txn_id, \"Transaction\");" +
      "P = SELECT t FROM St:s -(NEXT_TRANSACTION:e)-> t;" +
      "PRINT P;" +
      "}")
print("\nStep 2 - traversal from to_vertex:")
try:
    r = conn.gsql(q2)
    print("Result:", str(r)[:300])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])

conn.gsql("DROP QUERY shortestPath")

# Step 3: to_vertex with single-hop traversal and WHERE
q3 = ("USE GRAPH " + GN + nl +
      "CREATE OR REPLACE QUERY shortestPath(STRING start_txn_id, STRING end_txn_id) {" +
      "St = to_vertex(start_txn_id, \"Transaction\");" +
      "Tgt = to_vertex(end_txn_id, \"Transaction\");" +
      "P = SELECT t FROM St:s -(NEXT_TRANSACTION:e)-> t WHERE t.id == end_txn_id;" +
      "PRINT P;" +
      "}")
print("\nStep 3 - traversal with WHERE:")
try:
    r = conn.gsql(q3)
    print("Result:", str(r)[:300])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])

conn.gsql("DROP QUERY shortestPath")

# Step 4: try with ACCUM
q4 = ("USE GRAPH " + GN + nl +
      "CREATE OR REPLACE QUERY shortestPath(STRING start_txn_id, STRING end_txn_id) {" +
      "ListAccum<STRING> @@path;" +
      "St = to_vertex(start_txn_id, \"Transaction\");" +
      "P = SELECT t FROM St:s -(NEXT_TRANSACTION:e)-> t WHERE t.id == end_txn_id" +
      "    ACCUM @@path += t.id;" +
      "PRINT @@path;" +
      "}")
print("\nStep 4 - traversal with ACCUM:")
try:
    r = conn.gsql(q4)
    print("Result:", str(r)[:300])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])
