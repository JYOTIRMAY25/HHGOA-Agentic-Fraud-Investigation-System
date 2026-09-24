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

# Try different INSTALL QUERY syntaxes for template queries
tests = [
    "INSTALL QUERY all_path TEMPLATE FROM GDBMS_ALGO.path",
    "INSTALL QUERY all_path FROM GDBMS_ALGO.path",
    "CREATE OR REPLACE QUERY all_path(vertex v_source, vertex target_v, int depth, bool print_results, string file_path) TEMPLATE FOR GRAPH HHGOA_Fraud_Graph { }",
    # Try different variable-length edge syntaxes
    ("USE GRAPH " + GN + nl + "CREATE OR REPLACE QUERY t1(STRING s, STRING e) { Start = {Transaction.*}; P = SELECT t FROM Start -(NEXT_TRANSACTION*:1..10)-> t WHERE t.id == e ACCUM @@path += t.id; PRINT P; }"),
    ("USE GRAPH " + GN + nl + "CREATE OR REPLACE QUERY t2(STRING s, STRING e) { Start = {Transaction.*}; P = SELECT t FROM Start -(NEXT_TRANSACTION*:0..10)-> t WHERE t.id == e ACCUM @@path += t.id; PRINT P; }"),
]

for i, t in enumerate(tests):
    print("=== test " + str(i+1) + " ===")
    try:
        r = conn.gsql(t)
        print("Result:", str(r)[:300])
    except Exception as e:
        print("Error:", type(e).__name__, str(e)[:300])
    print()
