#!/usr/bin/env python3
"""Test GSQL query patterns and install queries."""
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

# Test 1: Simple query with attribute access using SELECT
q1 = '''CREATE OR REPLACE DISTRIBUTED QUERY test_attr1() FOR GRAPH HHGOA_Fraud_Graph {
    Start = {Transaction.*};
    Result = SELECT t FROM Start:t LIMIT 1;
    PRINT Result.amount, Result.risk_score;
}'''
print('=== Test 1: attribute access ===')
try:
    r = conn.installQueries(queries=q1)
    print('Result:', str(r)[:300])
except Exception as e:
    print('Error:', str(e)[:300])

# Test 2: WHERE with to_vertex
q2 = '''CREATE OR REPLACE DISTRIBUTED QUERY test_attr2() FOR GRAPH HHGOA_Fraud_Graph {
    Start = {Transaction.*};
    Result = SELECT t FROM Start:t WHERE t == to_vertex("3034450", "Transaction");
    PRINT Result;
}'''
print()
print('=== Test 2: WHERE with to_vertex ===')
try:
    r = conn.installQueries(queries=q2)
    print('Result:', str(r)[:300])
except Exception as e:
    print('Error:', str(e)[:300])

# Test 3: ACCUM with attribute
q3 = '''CREATE OR REPLACE DISTRIBUTED QUERY test_attr3() FOR GRAPH HHGOA_Fraud_Graph {
    SumAccum<INT> @@count = 0;
    Start = {Card.*};
    Start = SELECT c FROM Start:c ACCUM @@count += c.outdegree("PERFORMS");
    PRINT @@count;
}'''
print()
print('=== Test 3: ACCUM with attribute ===')
try:
    r = conn.installQueries(queries=q3)
    print('Result:', str(r)[:300])
except Exception as e:
    print('Error:', str(e)[:300])

# Test 4: Traversal
q4 = '''CREATE OR REPLACE DISTRIBUTED QUERY test_attr4() FOR GRAPH HHGOA_Fraud_Graph {
    VERTEX card;
    card = to_vertex("C05381-K2", "Card");
    Start = {card};
    CustomerSet = SELECT c FROM Start:s -(OWNED_BY:e)-> Customer:c;
    PRINT CustomerSet;
}'''
print()
print('=== Test 4: traversal ===')
try:
    r = conn.installQueries(queries=q4)
    print('Result:', str(r)[:300])
except Exception as e:
    print('Error:', str(e)[:300])