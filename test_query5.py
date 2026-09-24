#!/usr/bin/env python3
"""Test GSQL query patterns with gsql() method."""
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
q1 = 'USE GRAPH HHGOA_Fraud_Graph\nCREATE OR REPLACE DISTRIBUTED QUERY test_attr1() FOR GRAPH HHGOA_Fraud_Graph {\n    Start = {Transaction.*};\n    Result = SELECT t FROM Start:t LIMIT 1;\n    PRINT Result.amount, Result.risk_score;\n}'
print('=== Test 1: attribute access ===')
try:
    r = conn.gsql(q1)
    print('Result:', str(r)[:300])
except Exception as e:
    print('Error:', str(e)[:300])

# Test 2: WHERE with to_vertex
q2 = 'USE GRAPH HHGOA_Fraud_Graph\nCREATE OR REPLACE DISTRIBUTED QUERY test_attr2() FOR GRAPH HHGOA_Fraud_Graph {\n    Start = {Transaction.*};\n    Result = SELECT t FROM Start:t WHERE t == to_vertex("3034450", "Transaction");\n    PRINT Result;\n}'
print()
print('=== Test 2: WHERE with to_vertex ===')
try:
    r = conn.gsql(q2)
    print('Result:', str(r)[:300])
except Exception as e:
    print('Error:', str(e)[:300])

# Test 3: ACCUM with attribute
q3 = 'USE GRAPH HHGOA_Fraud_Graph\nCREATE OR REPLACE DISTRIBUTED QUERY test_attr3() FOR GRAPH HHGOA_Fraud_Graph {\n    SumAccum<INT> @@count = 0;\n    Start = {Card.*};\n    Start = SELECT c FROM Start:c ACCUM @@count += c.outdegree("PERFORMS");\n    PRINT @@count;\n}'
print()
print('=== Test 3: ACCUM with attribute ===')
try:
    r = conn.gsql(q3)
    print('Result:', str(r)[:300])
except Exception as e:
    print('Error:', str(e)[:300])

# Test 4: Traversal
q4 = 'USE GRAPH HHGOA_Fraud_Graph\nCREATE OR REPLACE DISTRIBUTED QUERY test_attr4() FOR GRAPH HHGOA_Fraud_Graph {\n    VERTEX card;\n    card = to_vertex("C05381-K2", "Card");\n    Start = {card};\n    CustomerSet = SELECT c FROM Start:s -(OWNED_BY:e)-> Customer:c;\n    PRINT CustomerSet;\n}'
print()
print('=== Test 4: traversal ===')
try:
    r = conn.gsql(q4)
    print('Result:', str(r)[:300])
except Exception as e:
    print('Error:', str(e)[:300])