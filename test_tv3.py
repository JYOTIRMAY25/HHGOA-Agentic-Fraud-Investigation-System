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

# Check to_vertex return type more carefully
tests = [
    # Try assigning to Vertex type variable
    "USE GRAPH HHGOA_Fraud_Graph\nCREATE OR REPLACE QUERY t1(STRING tid) { Vertex<Transaction> V = to_vertex(tid, \"Transaction\"); PRINT V; }",
    # Try using to_vertex in a WHERE clause
    "USE GRAPH HHGOA_Fraud_Graph\nCREATE OR REPLACE QUERY t2(STRING tid) { Start = {Transaction.*}; S = SELECT s FROM Start:s WHERE id(s) == tid; PRINT S; }",
    # Try using to_vertex with SetAccum
    "USE GRAPH HHGOA_Fraud_Graph\nCREATE OR REPLACE QUERY t3(STRING tid) { SetAccum<Vertex<Transaction>> S; S += to_vertex(tid, \"Transaction\"); PRINT S; }",
    # Try ListAccum approach
    "USE GRAPH HHGOA_Fraud_Graph\nCREATE OR REPLACE QUERY t4(STRING tid) { ListAccum<Vertex<Transaction>> S; S += to_vertex(tid, \"Transaction\"); PRINT S; }",
    # Try to_vertex in FROM clause
    "USE GRAPH HHGOA_Fraud_Graph\nCREATE OR REPLACE QUERY t5(STRING tid) { S = SELECT s FROM to_vertex(tid, \"Transaction\"):s; PRINT S; }",
]

for i, q in enumerate(tests):
    print(f"=== Test {i+1} ===")
    try:
        r = conn.gsql(q)
        print(f"Result: {str(r)[:300]}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)[:300]}")
    print()
