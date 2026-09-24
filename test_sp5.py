#!/usr/bin/env python3
"""Test more SP approaches."""
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
    ("tv_extract", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_tv(STRING tid) {{
  Src = to_vertex(tid, "Transaction");
  Start = SELECT s FROM Src:s;
  PRINT Start;
}}"""),
    ("sp_name1", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_sp(STRING sid, STRING eid) {{
  Src = to_vertex(sid, "Transaction");
  Tgt = to_vertex(eid, "Transaction");
  Path = shortestPath(Src, Tgt, "NEXT_TRANSACTION");
  PRINT Path;
}}"""),
    ("sp_name2", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_sp(STRING sid, STRING eid) {{
  Src = to_vertex(sid, "Transaction");
  Tgt = to_vertex(eid, "Transaction");
  Path = A shortest path FROM Src TO Tgt THROUGH "NEXT_TRANSACTION";
  PRINT Path;
}}"""),
    ("sp_simple", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_sp(STRING sid, STRING eid) {{
  Src = to_vertex(sid, "Transaction");
  Tgt = to_vertex(eid, "Transaction");
  Path = Src SHORTEST_PATH Tgt;
  PRINT Path;
}}"""),
    ("tv_with_type", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_tv(STRING tid) {{
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
