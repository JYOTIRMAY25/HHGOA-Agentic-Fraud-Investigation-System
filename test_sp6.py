#!/usr/bin/env python3
"""Test to_vertex usage and check available functions."""
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
    ("tv_from", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_tv(STRING tid) {{
  Result = SELECT t FROM to_vertex(tid, "Transaction")-(PERFORMS:e)-> t:Card;
  PRINT Result;
}}"""),
    ("tv_from_set", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_tv(STRING tid) {{
  Result = SELECT t FROM {{to_vertex(tid, "Transaction")}}-(PERFORMS:e)-> t:Card;
  PRINT Result;
}}"""),
    ("sp_algos", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_algos() {{
  ListAccum<STRING> @@funcs;
  @@funcs += "shortestPath";
  PRINT @@funcs;
}}"""),
    ("tv_simple", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_tv(STRING tid) {{
  V = to_vertex(tid, "Transaction");
  PRINT V;
}}"""),
    ("tv_collect2", f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_tv(STRING tid) {{
  Start = {{to_vertex(tid, "Transaction")}};
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
