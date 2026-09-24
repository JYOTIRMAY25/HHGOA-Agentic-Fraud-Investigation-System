#!/usr/bin/env python3
"""Test with different vertex types."""
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
    ("customer", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_c() {{
  Start = {{Customer.*}};
  PRINT Start;
}}"""),
    ("card", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_c() {{
  Start = {{Card.*}};
  PRINT Start;
}}"""),
    ("txn_rename", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_t(STRING tid) {{
  Start = {{Transaction.*}};
  T = SELECT s FROM Start:s WHERE s.id == tid;
  PRINT T;
}}"""),
    ("txn_with_acum", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_t2(STRING tid) {{
  ListAccum<STRING> @@path;
  Start = {{Transaction.*}};
  S = SELECT s FROM Start:s WHERE s.id == tid
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
