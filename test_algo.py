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

# Check available graph algorithms
print("=== Checking graph algorithms ===")
try:
    r = conn.gsql("USE GRAPH HHGOA_Fraud_Graph SHOW FUNCTION *")
    print("Functions:", str(r)[:500])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])

# Try installing graph algorithms
print("\n=== Try install algorithms ===")
try:
    r = conn.gsql("INSTALL FUNCTION ALL")
    print("Install functions:", str(r)[:300])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])

# Try listing UDFs
print("\n=== Try getUDF ===")
try:
    r = conn.getUDF()
    print("UDFs:", str(r)[:300])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])

# Try shortest path with different syntax
print("\n=== Try sp syntax ===")
sp_queries = [
    "USE GRAPH HHGOA_Fraud_Graph CREATE OR REPLACE QUERY sp(STRING s, STRING e) { Start = {Transaction.*}; P = Start SHORTEST_PATH TO End; PRINT P; }",
    "USE GRAPH HHGOA_Fraud_Graph CREATE OR REPLACE QUERY sp(STRING s, STRING e) { Start = {Transaction.*}; End = {Transaction.*}; P = shortestPath(Start, End, \"NEXT_TRANSACTION\"); PRINT P; }",
    "USE GRAPH HHGOA_Fraud_Graph CREATE OR REPLACE QUERY sp(STRING s, STRING e) { Start = {Transaction.*}; End = {Transaction.*}; P = Start -NEXT_TRANSACTION*-> End; PRINT P; }",
]
for i, q in enumerate(sp_queries):
    print(f"--- SP query {i+1} ---")
    try:
        r = conn.gsql(q)
        print("Result:", str(r)[:200])
    except Exception as e:
        print("Error:", type(e).__name__, str(e)[:200])
