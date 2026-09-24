#!/usr/bin/env python3
"""Deploy shortestPath query with proper formatting."""
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
conn.useGraph(graphname)

# Deploy shortestPath query - GSQL needs proper newlines for multi-line constructs
query = """CREATE QUERY shortestPath(STRING start_txn_id, STRING end_txn_id) FOR HHGOA_Fraud_Graph {
  List<Transaction> path;
  FLOAT total_distance = 0.0;
  Start = {SELECT t FROM Transaction:t WHERE t.transaction_id == start_txn_id};
  End = {SELECT t FROM Transaction:t WHERE t.transaction_id == end_txn_id};
  path = tgb_shortest_path(Start, End, "NEXT_TRANSACTION");
  IF (total_distance < 10000) THEN
    PRINT path;
  END;
}"""

print("Deploying shortestPath query...")
print(f"Query preview:\n{query[:200]}...")
try:
    r = conn.gsql(query)
    print(f"Result: {r}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)[:300]}")

# Verify
print("\nVerifying...")
try:
    r = conn.showQuery("shortestPath")
    print(f"showQuery: {r}")
except Exception as e:
    print(f"showQuery error: {type(e).__name__}: {str(e)[:200]}")
