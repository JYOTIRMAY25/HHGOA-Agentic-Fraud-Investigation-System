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

# Test 1: Simple query without USE GRAPH
q1 = 'CREATE OR REPLACE DISTRIBUTED QUERY test_attr1() FOR GRAPH HHGOA_Fraud_Graph {\n    Start = {Transaction.*};\n    Result = SELECT t FROM Start:t LIMIT 1;\n    PRINT Result.amount, Result.risk_score;\n}'
print('=== Test 1: no USE GRAPH ===')
try:
    r = conn.gsql(q1)
    print('Result:', str(r)[:300])
except Exception as e:
    print('Error:', str(e)[:300])

# Test 2: Simple query with USE GRAPH
q2 = 'USE GRAPH HHGOA_Fraud_Graph\nCREATE OR REPLACE DISTRIBUTED QUERY test_attr2() FOR GRAPH HHGOA_Fraud_Graph {\n    Start = {Transaction.*};\n    Result = SELECT t FROM Start:t LIMIT 1;\n    PRINT Result.amount, Result.risk_score;\n}'
print()
print('=== Test 2: with USE GRAPH ===')
try:
    r = conn.gsql(q2)
    print('Result:', str(r)[:300])
except Exception as e:
    print('Error:', str(e)[:300])

# Test 3: Just CREATE QUERY (no DISTRIBUTED)
q3 = 'USE GRAPH HHGOA_Fraud_Graph\nCREATE OR REPLACE QUERY test_attr3() FOR GRAPH HHGOA_Fraud_Graph {\n    Start = {Transaction.*};\n    Result = SELECT t FROM Start:t LIMIT 1;\n    PRINT Result.amount, Result.risk_score;\n}'
print()
print('=== Test 3: CREATE QUERY (no DISTRIBUTED) ===')
try:
    r = conn.gsql(q3)
    print('Result:', str(r)[:300])
except Exception as e:
    print('Error:', str(e)[:300])

# Test 4: Check what SHOW VERTEX returns
print()
print('=== SHOW VERTEX Transaction ===')
r = conn.gsql('SHOW VERTEX Transaction')
print(str(r)[:500])