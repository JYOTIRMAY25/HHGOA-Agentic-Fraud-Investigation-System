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

GN = graphname
nl = chr(10)

tests = [
    ("tgb_sp1", "USE GRAPH HHGOA_Fraud_Graph CREATE OR REPLACE QUERY t1(STRING s, STRING e) { St = to_vertex(s, \"Customer\"); Tgt = to_vertex(e, \"Customer\"); P = tgb_shortest_path(St, Tgt, \"PERFORMS\"); PRINT P; }"),
    ("tgb_sp2", "USE GRAPH HHGOA_Fraud_Graph CREATE OR REPLACE QUERY t2(STRING s, STRING e) { St = to_vertex(s, \"Customer\"); Tgt = to_vertex(e, \"Customer\"); P = tgb_shortest_path(St, Tgt, \"PERFORMS\", 10); PRINT P; }"),
    ("dijkstra1", "USE GRAPH HHGOA_Fraud_Graph CREATE OR REPLACE QUERY t3(STRING s, STRING e) { St = to_vertex(s, \"Customer\"); Tgt = to_vertex(e, \"Customer\"); P = tgb_dijkstra(St, Tgt, \"PERFORMS\"); PRINT P; }"),
    ("dijkstra2", "USE GRAPH HHGOA_Fraud_Graph CREATE OR REPLACE QUERY t4(STRING s, STRING e) { St = to_vertex(s, \"Customer\"); Tgt = to_vertex(e, \"Customer\"); P = dijkstra(St, Tgt, \"PERFORMS\"); PRINT P; }"),
    ("sp_keyword", "USE GRAPH HHGOA_Fraud_Graph CREATE OR REPLACE QUERY t5(STRING s, STRING e) { St = to_vertex(s, \"Customer\"); Dst = to_vertex(e, \"Customer\"); P = tgb_shortest_path(St, Dst, \"PERFORMS\"); PRINT P; }"),
]

for label, q in tests:
    print("=== " + label + " ===")
    try:
        r = conn.gsql(q)
        print("Result:", str(r)[:300])
    except Exception as e:
        print("Error:", type(e).__name__, str(e)[:300])
    print()
