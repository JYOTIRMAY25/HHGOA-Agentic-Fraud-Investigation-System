#!/usr/bin/env python3
"""Deploy shortestPath using various methods."""
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

# Method 1: Include USE GRAPH in the same command
print("Method 1: USE GRAPH + CREATE QUERY in one command")
query = f"""USE GRAPH {graphname}
CREATE QUERY shortestPath(STRING start_txn_id, STRING end_txn_id) FOR GRAPH {graphname} {{
  List<Transaction> path;
  FLOAT total_distance = 0.0;
  Start = {{SELECT t FROM Transaction:t WHERE t.transaction_id == start_txn_id}};
  End = {{SELECT t FROM Transaction:t WHERE t.transaction_id == end_txn_id}};
  path = tgb_shortest_path(Start, End, "NEXT_TRANSACTION");
  IF (total_distance < 10000) THEN
    PRINT path;
  END;
}}"""
try:
    r = conn.gsql(query)
    print(f"Result: {r}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)[:300]}")

print("\nMethod 2: Just CREATE QUERY with graph context")
query2 = f"CREATE QUERY shortestPath(STRING start_txn_id, STRING end_txn_id) FOR GRAPH {graphname} {{ List<Transaction> path; FLOAT total_distance = 0.0; Start = {{SELECT t FROM Transaction:t WHERE t.transaction_id == start_txn_id}}; End = {{SELECT t FROM Transaction:t WHERE t.transaction_id == end_txn_id}}; path = tgb_shortest_path(Start, End, \"NEXT_TRANSACTION\"); IF (total_distance < 10000) THEN PRINT path; END; }}"
try:
    r = conn.gsql(query2)
    print(f"Result: {r}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)[:300]}")

print("\nMethod 3: Using createQuery API")
try:
    r = conn.createQuery("shortestPath", "start_txn_id STRING, end_txn_id STRING", "transaction_id STRING", graphname)
    print(f"createQuery: {r}")
except Exception as e:
    print(f"createQuery error: {type(e).__name__}: {str(e)[:300]}")
