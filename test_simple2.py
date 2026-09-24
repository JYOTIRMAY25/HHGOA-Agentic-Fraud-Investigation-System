#!/usr/bin/env python3
"""Test simpler query approaches."""
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
    ("simple_select", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_s(STRING tid) {{
  S = SELECT t FROM Transaction:t WHERE id(t) == tid;
  PRINT S;
}}"""),
    ("simple_select2", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_s2(STRING tid) {{
  S = SELECT t FROM Transaction:t WHERE t.id == tid;
  PRINT S;
}}"""),
    ("tv_iterate", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_tv(STRING tid) {{
  Start = to_vertex(tid, "Transaction");
  S = SELECT s FROM Start:s;
  PRINT S;
}}"""),
    ("tv_single", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_tvs(STRING tid) {{
  Start = to_vertex(tid, "Transaction");
  PRINT Start;
}}"""),
    ("accum_simple", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_acc(STRING tid) {{
  ListAccum<STRING> @@path;
  Start = to_vertex(tid, "Transaction");
  S = SELECT s FROM Start:s;
  @@path += s.id;
  PRINT @@path;
}}"""),
]

for label, q in tests:
    print(f"=== {label} ===")
    try:
        r = conn.gsql(q)
        print(f"Result: {str(r)[:300]}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)[:300]}")
    print()
