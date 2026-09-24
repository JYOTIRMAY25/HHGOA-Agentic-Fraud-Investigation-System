#!/usr/bin/env python3
"""Test shortest path with graph context."""
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

base = f"USE GRAPH {graphname}; "

tests = [
    ("to_vertex", base + 'CREATE OR REPLACE QUERY test_tv(STRING tid) { Start = to_vertex(tid, "Transaction"); PRINT Start; }'),
    ("tgb_shortest_path", base + 'CREATE OR REPLACE QUERY test_sp(STRING s, STRING e) { Start = to_vertex(s, "Transaction"); End = to_vertex(e, "Transaction"); Path = tgb_shortest_path(Start, End, "NEXT_TRANSACTION"); PRINT Path; }'),
    ("sp_function", base + 'CREATE OR REPLACE QUERY test_sp2(STRING s, STRING e) { Start = to_vertex(s, "Transaction"); End = to_vertex(e, "Transaction"); Path = shortestPath(Start, End, "NEXT_TRANSACTION"); PRINT Path; }'),
    ("with_dist", base + 'CREATE OR REPLACE QUERY test_sp3(STRING s, STRING e) { ListAccum<STRING> @@path; FloatAccum @@td = 0.0; Start = to_vertex(s, "Transaction"); End = to_vertex(e, "Transaction"); Path = tgb_shortest_path(Start, End, "NEXT_TRANSACTION"); @@path += Path; PRINT Path, @@path; }'),
]

for label, q in tests:
    print(f"=== {label} ===")
    try:
        r = conn.gsql(q)
        print(f"Result: {str(r)[:400]}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)[:400]}")
    print()
