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

nl = chr(10)
GN = graphname

tests = [
    ("customer_tv", "USE GRAPH " + GN + nl + "CREATE OR REPLACE QUERY tc(STRING tid) { S = to_vertex(tid, \"Customer\"); PRINT S; }"),
    ("customer_select", "USE GRAPH " + GN + nl + "CREATE OR REPLACE QUERY tc2(STRING tid) { S = {Customer.*}; R = SELECT s FROM S:s WHERE s.id == tid; PRINT R; }"),
    ("customer_tv_acc", "USE GRAPH " + GN + nl + "CREATE OR REPLACE QUERY tc3(STRING tid) { ListAccum<STRING> @@path; S = to_vertex(tid, \"Customer\"); R = SELECT s FROM S:s; @@path += s.id; PRINT @@path; }"),
]

for label, q in tests:
    print("=== " + label + " ===")
    try:
        r = conn.gsql(q)
        print("Result:", str(r)[:300])
    except Exception as e:
        print("Error:", type(e).__name__, str(e)[:300])
    print()
