#!/usr/bin/env python3
"""Test with different graph context."""
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

# Test 1: Basic query without vertex references
tests = [
    ("no_vertex", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_n() {{
  INT x = 1;
  PRINT x;
}}"""),
    ("to_vertex_only", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_tv(STRING tid) {{
  Start = to_vertex(tid, "Transaction");
  PRINT Start;
}}"""),
    ("to_vertex_set", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_tvs(STRING tid) {{
  Start = to_vertex(tid, "Transaction");
  S = SELECT s FROM Start:s;
  PRINT S;
}}"""),
    ("accum_test", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_acc(STRING tid) {{
  ListAccum<STRING> @@path;
  Start = to_vertex(tid, "Transaction");
  S = SELECT s FROM Start:s;
  ACCUM @@path += s.id;
  PRINT @@path;
}}"""),
]

for label, q in tests:
    print(f"=== {label} ===")
    try:
        r = conn.gsql(q)
        print(f"Result: {str(r)[:400]}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)[:400]}")
    print()
