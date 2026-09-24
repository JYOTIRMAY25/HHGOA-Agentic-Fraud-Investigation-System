#!/usr/bin/env python3
"""Try to fix shortestPath query."""
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

# Try query using id() function instead of attribute
queries = [
    ("DROP", "DROP QUERY shortestPath"),
    ("try1", """CREATE OR REPLACE QUERY shortestPath(STRING start_txn_id, STRING end_txn_id) FOR GRAPH HHGOA_Fraud_Graph {
    ListAccum<STRING> @@path;
    Start = {Transaction.*};
    Src = SELECT s FROM Start:s WHERE id(s) == start_txn_id;
    Tgt = SELECT t FROM Src:s -(NEXT_TRANSACTION:e)-> t WHERE id(t) == end_txn_id
        ACCUM @@path += t.transaction_id;
    PRINT @@path AS path;
}"""),
    ("try2", """CREATE OR REPLACE QUERY shortestPath(STRING start_txn_id, STRING end_txn_id) FOR GRAPH HHGOA_Fraud_Graph {
    ListAccum<STRING> @@path;
    Start = {Transaction.*};
    Src = SELECT s FROM Start:t WHERE t.transaction_id == start_txn_id;
    Tgt = SELECT t FROM Src:s -(NEXT_TRANSACTION:e)-> t WHERE t.transaction_id == end_txn_id
        ACCUM @@path += t.transaction_id;
    PRINT @@path AS path;
}"""),
    ("try3", """CREATE OR REPLACE QUERY shortestPath(STRING start_txn_id, STRING end_txn_id) FOR GRAPH HHGOA_Fraud_Graph {
    ListAccum<STRING> @@path;
    Start = {Transaction.*};
    Src = SELECT s FROM Start:t ACCUM @@path += s.transaction_id;
    PRINT @@path AS path;
}"""),
]

for label, q in queries:
    if label == "DROP":
        print(f"=== {label} ===")
        try:
            r = conn.gsql(q)
            print(f"  Result: {r}")
        except Exception as e:
            print(f"  Error: {e}")
        continue
    
    print(f"=== {label} ===")
    try:
        r = conn.gsql(q)
        print(f"  Result: {str(r)[:300]}")
    except Exception as e:
        print(f"  Error: {type(e).__name__}: {str(e)[:300]}")

# Check status
print("\nStatus:")
try:
    r = conn.getQueryInfo("shortestPath")
    res = r.get('results', [])
    if res:
        print(f"  Status: {res[0].get('status')}, Error: {res[0].get('error')}")
except Exception as e:
    print(f"  Error: {e}")
