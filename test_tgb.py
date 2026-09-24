#!/usr/bin/env python3
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

# Check packages and functions
print("=== Packages ===")
try:
    r = conn.gsql("SHOW PACKAGE *")
    print("Packages:", str(r)[:500])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])

# Try tgb_shortest_path with different syntax
print("\n=== tgb_shortest_path attempts ===")
GN = graphname
nl = chr(10)
tgb_queries = [
    "USE GRAPH HHGOA_Fraud_Graph CREATE OR REPLACE QUERY t1(STRING s, STRING e) { Start = to_vertex(s, \"Customer\"); End = to_vertex(e, \"Customer\"); P = tgb_shortest_path(Start, End, \"PERFORMS\"); PRINT P; }",
    "USE GRAPH HHGOA_Fraud_Graph CREATE OR REPLACE QUERY t2(STRING s, STRING e) { Start = to_vertex(s, \"Customer\"); End = to_vertex(e, \"Customer\"); P = tgb_shortest_path(Start, End, \"PERFORMS\", 10); PRINT P; }",
    "USE GRAPH HHGOA_Fraud_Graph CREATE OR REPLACE QUERY t3(STRING s, STRING e) { Start = to_vertex(s, \"Customer\"); End = to_vertex(e, \"Customer\"); P = tgb_dijkstra(Start, End, \"PERFORMS\"); PRINT P; }",
    "USE GRAPH HHGOA_Fraud_Graph CREATE OR REPLACE QUERY t4(STRING s, STRING e) { Start = to_vertex(s, \"Customer\"); End = to_vertex(e, \"Customer\"); P = dijkstra(Start, End, \"PERFORMS\"); PRINT P; }",
    "USE GRAPH HHGOA_Fraud_Graph CREATE OR REPLACE QUERY t5(STRING s, STRING e) { Start = to_vertex(s, \"Customer\"); End = to_vertex(e, \"Customer\"); P = A shortest path from Start to End through \"PERFORMS\"; PRINT P; }",
]
for i, q in enumerate(tgb_queries):
    print(f"--- tgb query {i+1} ---")
    try:
        r = conn.gsql(q)
        print("Result:", str(r)[:200])
    except Exception as e:
        print("Error:", type(e).__name__, str(e)[:200])
