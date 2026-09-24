#!/usr/bin/env python3
"""Deploy corrected shortestPath query with graph context."""
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

# Include USE GRAPH in the same command
query = f"""USE GRAPH {graphname};
CREATE OR REPLACE QUERY shortestPath(STRING start_txn_id, STRING end_txn_id) FOR GRAPH {graphname} {{
    ListAccum<STRING> @@path;
    SumAccum<INT> @@hop_count = 0;

    Start = {{SELECT t FROM Transaction:t WHERE t.transaction_id == start_txn_id}};
    End = {{SELECT t FROM Transaction:t WHERE t.transaction_id == end_txn_id}};

    Path = SELECT t FROM Start -(NEXT_TRANSACTION*1..10)-> t WHERE t.transaction_id == end_txn_id
        ACCUM @@path += t.transaction_id,
             @@hop_count += 1;

    IF @@hop_count < 10000 THEN
        PRINT @@path AS path, @@hop_count AS hop_count;
    END;
}}"""

print("Deploying corrected query...")
try:
    r = conn.gsql(query)
    print(f"Result: {str(r)[:500]}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)[:500]}")

# Verify
print("\nVerifying...")
try:
    r = conn.showQuery("shortestPath")
    print(f"showQuery: {str(r)[:500]}")
except Exception as e:
    print(f"showQuery error: {type(e).__name__}: {str(e)[:200]}")
