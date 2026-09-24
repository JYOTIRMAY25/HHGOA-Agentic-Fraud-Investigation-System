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

# Try interpreted query without name
q = """USE GRAPH HHGOA_Fraud_Graph
INTERPRET QUERY (STRING tid) {
  Start = to_vertex(tid, "Customer");
  PRINT Start;
}"""

print("=== interpreted no name ===")
try:
    r = conn.gsql(q)
    print("Result:", str(r)[:300])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])

# Try runInterpretedQuery
print("\n=== runInterpretedQuery ===")
try:
    r = conn.runInterpretedQuery("INTERPRET QUERY (STRING tid) { Start = to_vertex(tid, \"Customer\"); PRINT Start; }")
    print("Result:", str(r)[:300])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])

# Try to_vertex with different syntax
q2 = "USE GRAPH HHGOA_Fraud_Graph CREATE OR REPLACE QUERY t(STRING tid) { Start = {to_vertex(tid, \"Customer\")}; PRINT Start; }"
print("\n=== braces ===")
try:
    r = conn.gsql(q2)
    print("Result:", str(r)[:300])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])
