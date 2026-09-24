#!/usr/bin/env python3
"""Test GSQL query patterns that work with this TigerGraph version."""
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

tests = [
    ("DISTRIBUTED QUERY + to_vertex",
     'USE GRAPH HHGOA_Fraud_Graph\n'
     'CREATE OR REPLACE DISTRIBUTED QUERY test_distributed() FOR GRAPH HHGOA_Fraud_Graph {\n'
     '    VERTEX txn;\n'
     '    txn = to_vertex("3034450", "Transaction");\n'
     '    Start = {txn};\n'
     '    PRINT Start;\n'
     '}'),

    ("DISTRIBUTED QUERY + WHERE + to_vertex",
     'USE GRAPH HHGOA_Fraud_Graph\n'
     'CREATE OR REPLACE DISTRIBUTED QUERY test_distributed2() FOR GRAPH HHGOA_Fraud_Graph {\n'
     '    Start = {Transaction.*};\n'
     '    Result = SELECT t FROM Start:t WHERE t == to_vertex("3034450", "Transaction");\n'
     '    PRINT Result;\n'
     '}'),

    ("DISTRIBUTED QUERY + ACCUM + attribute",
     'USE GRAPH HHGOA_Fraud_Graph\n'
     'CREATE OR REPLACE DISTRIBUTED QUERY test_distributed3() FOR GRAPH HHGOA_Fraud_Graph {\n'
     '    SumAccum<INT> @@count = 0;\n'
     '    Start = {Card.*};\n'
     '    Start = SELECT c FROM Start:c ACCUM @@count += c.outdegree("PERFORMS");\n'
     '    PRINT @@count;\n'
     '}'),

    ("DISTRIBUTED QUERY + traversal",
     'USE GRAPH HHGOA_Fraud_Graph\n'
     'CREATE OR REPLACE DISTRIBUTED QUERY test_distributed4() FOR GRAPH HHGOA_Fraud_Graph {\n'
     '    VERTEX card;\n'
     '    card = to_vertex("C05381-K2", "Card");\n'
     '    Start = {card};\n'
     '    CustomerSet = SELECT c FROM Start:s -(OWNED_BY:e)-> Customer:c;\n'
     '    PRINT CustomerSet;\n'
     '}'),

    ("DISTRIBUTED QUERY + PRINT alias",
     'USE GRAPH HHGOA_Fraud_Graph\n'
     'CREATE OR REPLACE DISTRIBUTED QUERY test_distributed5() FOR GRAPH HHGOA_Fraud_Graph {\n'
     '    VERTEX txn;\n'
     '    txn = to_vertex("3034450", "Transaction");\n'
     '    Start = {txn};\n'
     '    PRINT Start AS result;\n'
     '}'),
]

for name, q in tests:
    print(f'=== {name} ===')
    try:
        r = conn.gsql(q)
        print(f'  Result: {str(r)[:300]}')
    except Exception as e:
        print(f'  Error: {str(e)[:300]}')
    print()