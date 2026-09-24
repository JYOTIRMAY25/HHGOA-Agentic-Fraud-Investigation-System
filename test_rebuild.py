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

# Try rebuild
print("Trying rebuildGraph...")
try:
    r = conn.rebuildGraph()
    print("Result:", str(r)[:300])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])

# Check after rebuild
print("\nChecking getVertexTypes after rebuild...")
try:
    r = conn.getVertexTypes()
    print("Vertex types:", r)
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:200])

# Try running SHOW VERTEX without semicolon
print("\nTrying SHOW VERTEX without semicolon...")
try:
    r = conn.gsql("USE GRAPH HHGOA_Fraud_Graph SHOW VERTEX *")
    print("Result:", str(r)[:300])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])

# Try SCHEMA change job
print("\nTrying createSchemaChangeJob...")
try:
    r = conn.createSchemaChangeJob("test_scg", "HHGOA_Fraud_Graph")
    print("Result:", str(r)[:300])
except Exception as e:
    print("Error:", type(e).__name__, str(e)[:300])
