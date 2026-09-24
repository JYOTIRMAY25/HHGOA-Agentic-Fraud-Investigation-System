#!/usr/bin/env python3
"""Test shortest path approaches."""
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

tests = [
    ("to_vertex", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_tv(STRING tid) {{
  Start = to_vertex(tid, "Transaction");
  PRINT Start;
}}"""),
    ("tgb_sp", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_sp(STRING s, STRING e) {{
  Start = to_vertex(s, "Transaction");
  End = to_vertex(e, "Transaction");
  Path = tgb_shortest_path(Start, End, "NEXT_TRANSACTION");
  PRINT Path;
}}"""),
    ("sp_builtin", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_sp2(STRING s, STRING e) {{
  Start = to_vertex(s, "Transaction");
  End = to_vertex(e, "Transaction");
  Path = shortestPath(Start, End, "NEXT_TRANSACTION");
  PRINT Path;
}}"""),
    ("try_to_vertex_no_quotes", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_tv2(STRING tid) {{
  Start = to_vertex(tid, Transaction);
  PRINT Start;
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
