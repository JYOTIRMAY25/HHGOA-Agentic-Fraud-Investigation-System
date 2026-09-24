#!/usr/bin/env python3
"""Test installQueries method."""
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

# Try installing with file
print('=== installQueries with file ===')
try:
    r = conn.installQueries(file='D:/task4/tigergraph/gsql/validate_queries.gsql')
    print('Result:', str(r)[:500])
except Exception as e:
    print('Error:', str(e)[:500])

# Try installing with query string
print()
print('=== installQueries with query string ===')
q = 'CREATE OR REPLACE DISTRIBUTED QUERY test_install() FOR GRAPH HHGOA_Fraud_Graph {\n    VERTEX txn;\n    txn = to_vertex("3034450", "Transaction");\n    Start = {txn};\n    PRINT Start;\n}'
try:
    r = conn.installQueries(query=q)
    print('Result:', str(r)[:500])
except Exception as e:
    print('Error:', str(e)[:500])

# Check installed
print()
print('=== Query names ===')
r = conn.listQueryNames()
for q in sorted(r):
    print(q)