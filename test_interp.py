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
    ("interpreted_tv", "USE GRAPH " + GN + nl + "INTERPRET QUERY t(STRING tid) { Start = to_vertex(tid, \"Customer\"); PRINT Start; }"),
    ("interpreted_tv_acc", "USE GRAPH " + GN + nl + "INTERPRET QUERY t(STRING tid) { ListAccum<STRING> @@path; Start = to_vertex(tid, \"Customer\"); @@path += Start.id; PRINT @@path; }"),
    ("interpreted_select", "USE GRAPH " + GN + nl + "INTERPRET QUERY t(STRING tid) { Start = {Customer.*}; S = SELECT s FROM Start:s WHERE s.id == tid; PRINT S; }"),
]

for label, q in tests:
    print("=== " + label + " ===")
    try:
        r = conn.gsql(q)
        print("Result:", str(r)[:300])
    except Exception as e:
        print("Error:", type(e).__name__, str(e)[:300])
    print()
