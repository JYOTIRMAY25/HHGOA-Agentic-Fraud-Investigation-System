#!/usr/bin/env python3
"""Test vertex resolution and SP function names."""
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
    ("tv_with_id", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_tv(STRING tid) {{
  Start = {{Transaction.*}};
  Src = SELECT s FROM Start:s WHERE s.id == tid;
  PRINT Src;
}}"""),
    ("sp_getpath", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_sp(STRING sid, STRING eid) {{
  Src = {{Transaction.*}};
  S = SELECT s FROM Src:s WHERE s.id == sid;
  Tgt = SELECT t FROM S:s -(NEXT_TRANSACTION*1..10)-> t WHERE t.id == eid;
  PRINT S, Tgt;
}}"""),
    ("sp_getpath2", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_sp(STRING sid, STRING eid) {{
  Src = {{Transaction.*}};
  S = SELECT s FROM Src:s WHERE s.id == sid;
  Tgt = SELECT t FROM S:s -(NEXT_TRANSACTION:e)-> t WHERE t.id == eid
      ACCUM @@path += t.id;
  PRINT S, Tgt;
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
