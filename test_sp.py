#!/usr/bin/env python3
"""Test shortest path approaches in TigerGraph."""
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

# Test 1: Check if to_vertex exists
print("=== Test 1: to_vertex ===")
try:
    r = conn.gsql('CREATE OR REPLACE QUERY test_tv(STRING tid) FOR GRAPH HHGOA_Fraud_Graph { Start = to_vertex(tid, "Transaction"); PRINT Start; }')
    print(f"Result: {str(r)[:300]}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)[:300]}")

# Test 2: Check tgb_shortest_path
print("\n=== Test 2: tgb_shortest_path ===")
try:
    r = conn.gsql('CREATE OR REPLACE QUERY test_sp(STRING start_id, STRING end_id) FOR GRAPH HHGOA_Fraud_Graph { Start = to_vertex(start_id, "Transaction"); End = to_vertex(end_id, "Transaction"); Path = tgb_shortest_path(Start, End, "NEXT_TRANSACTION"); PRINT Path; }')
    print(f"Result: {str(r)[:300]}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)[:300]}")

# Test 3: Try shortestPath (function from graph algorithms)
print("\n=== Test 3: shortestPath function ===")
try:
    r = conn.gsql('CREATE OR REPLACE QUERY test_sp2(STRING start_id, STRING end_id) FOR GRAPH HHGOA_Fraud_Graph { Start = to_vertex(start_id, "Transaction"); End = to_vertex(end_id, "Transaction"); Path = shortestPath(Start, End, "NEXT_TRANSACTION"); PRINT Path; }')
    print(f"Result: {str(r)[:300]}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)[:300]}")

# Test 4: Try with accumulated distance
print("\n=== Test 4: With distance accumulation ===")
try:
    r = conn.gsql('CREATE OR REPLACE QUERY test_sp3(STRING start_id, STRING end_id) FOR GRAPH HHGOA_Fraud_Graph { ListAccum<STRING> @@path; FloatAccum @@total_distance = 0.0; Start = to_vertex(start_id, "Transaction"); End = to_vertex(end_id, "Transaction"); Path = tgb_shortest_path(Start, End, "NEXT_TRANSACTION"); @@path += Path; PRINT Path, @@path; }')
    print(f"Result: {str(r)[:300]}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)[:300]}")
