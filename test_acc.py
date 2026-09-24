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
    ("listacc_vertex", "USE GRAPH " + GN + nl + "CREATE OR REPLACE QUERY t1(STRING tid) { ListAccum<Vertex<>> @@v; S = to_vertex(tid, \"Customer\"); @@v += S; PRINT @@v; }"),
    ("listacc_vertex2", "USE GRAPH " + GN + nl + "CREATE OR REPLACE QUERY t2(STRING tid) { ListAccum<STRING> @@path; S = to_vertex(tid, \"Customer\"); @@path += S.id; PRINT @@path; }"),
    ("vertex_set_var", "USE GRAPH " + GN + nl + "CREATE OR REPLACE QUERY t3(STRING tid) { Vertex<Customer> S = to_vertex(tid, \"Customer\"); PRINT S; }"),
    ("getvertex_api", "USE GRAPH " + GN + nl + "CREATE OR REPLACE QUERY t4(STRING tid) { S = SELECT s FROM Customer:s WHERE s.id == tid; PRINT S; }"),
]

for label, q in tests:
    print("=== " + label + " ===")
    try:
        r = conn.gsql(q)
        print("Result:", str(r)[:300])
    except Exception as e:
        print("Error:", type(e).__name__, str(e)[:300])
    print()
