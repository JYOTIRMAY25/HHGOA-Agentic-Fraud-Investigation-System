#!/usr/bin/env python3
"""Simple query test."""
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

# Simple test
q = f"""USE GRAPH {graphname}
CREATE OR REPLACE QUERY test_simple() {{
  Start = {{Transaction.*}};
  PRINT Start;
}}"""

print("Testing simple query...")
try:
    r = conn.gsql(q)
    print(f"Result: {str(r)[:400]}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)[:400]}")

# Check vertex types via API
print("\nChecking graph schema via API...")
try:
    r = conn.gsql(f"USE GRAPH {graphname}; SHOW SCHEMA")
    print(f"Schema: {str(r)[:500]}")
except Exception as e:
    print(f"Schema error: {type(e).__name__}: {str(e)[:300]}")

# Check getVertexTypes
print("\nChecking getVertexTypes...")
try:
    r = conn.getVertexTypes()
    print(f"Vertex types: {r}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)[:300]}")

# Check getEdgeTypes
print("\nChecking getEdgeTypes...")
try:
    r = conn.getEdgeTypes()
    print(f"Edge types: {r}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)[:300]}")
