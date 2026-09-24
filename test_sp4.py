#!/usr/bin/env python3
"""Test shortest path - fix types and keywords."""
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
    ("tv_braces", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_tv(STRING tid) {{
  Start = {{to_vertex(tid, "Transaction")}};
  PRINT Start;
}}"""),
    ("tv_select", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_tv(STRING tid) {{
  Start = SELECT s FROM to_vertex(tid, "Transaction"):s;
  PRINT Start;
}}"""),
    ("tv_collect", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_tv(STRING tid) {{
  Start = COLLECT s FROM to_vertex(tid, "Transaction"):s INTO s;
  PRINT Start;
}}"""),
    ("sp_rename", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_sp(STRING sid, STRING eid) {{
  Src = to_vertex(sid, "Transaction");
  Tgt = to_vertex(eid, "Transaction");
  Path = tgb_shortest_path(Src, Tgt, "NEXT_TRANSACTION");
  PRINT Path;
}}"""),
    ("sp_vset", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_sp2(STRING sid, STRING eid) {{
  Src = {{to_vertex(sid, "Transaction")}};
  Tgt = {{to_vertex(eid, "Transaction")}};
  Path = tgb_shortest_path(Src, Tgt, "NEXT_TRANSACTION");
  PRINT Path;
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
