#!/usr/bin/env python3
"""Test to_vertex in various contexts."""
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
    ("tv_in_from", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_tv(STRING tid) {{
  Start = SELECT t FROM Transaction:t WHERE id(t) == tid;
  PRINT Start;
}}"""),
    ("tv_from_vertex", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_tv(STRING tid) {{
  Start = SELECT t FROM Transaction:t WHERE t.id == tid;
  PRINT Start;
}}"""),
    ("tv_with_id_func", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_tv(STRING tid) {{
  Start = SELECT t FROM Transaction:t WHERE id(t) == tid;
  PRINT Start;
}}"""),
    ("to_vertex_from", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_tv(STRING tid) {{
  Start = SELECT s FROM to_vertex(tid, "Transaction"):s;
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
