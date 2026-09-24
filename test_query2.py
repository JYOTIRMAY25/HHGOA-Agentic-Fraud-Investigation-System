#!/usr/bin/env python3
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

# Test with id() function for primary_id
q = 'USE GRAPH HHGOA_Fraud_Graph\nCREATE OR REPLACE QUERY test_vertex3() FOR GRAPH HHGOA_Fraud_Graph {\n    Start = {Card.*};\n    Source = SELECT c FROM Start:c WHERE id(c) == "C00001-K1";\n    PRINT Source;\n}'
r = conn.gsql(q)
print('Vertex query with id():', str(r)[:500])

# Test with attribute access in ACCUM
q2 = 'USE GRAPH HHGOA_Fraud_Graph\nCREATE OR REPLACE QUERY test_vertex4() FOR GRAPH HHGOA_Fraud_Graph {\n    SumAccum<INT> @@count = 0;\n    Start = {Card.*};\n    Source = SELECT c FROM Start:c WHERE id(c) == "C00001-K1" ACCUM @@count += 1;\n    PRINT @@count;\n}'
r = conn.gsql(q2)
print('Vertex query with ACCUM:', str(r)[:500])

# Test with traversal
q3 = 'USE GRAPH HHGOA_Fraud_Graph\nCREATE OR REPLACE QUERY test_vertex5() FOR GRAPH HHGOA_Fraud_Graph {\n    Start = {Card.*};\n    Source = SELECT c FROM Start:c WHERE id(c) == "C00001-K1";\n    Txns = SELECT t FROM Source:c -(PERFORMS:e)-> Transaction:t;\n    PRINT Txns;\n}'
r = conn.gsql(q3)
print('Vertex query with traversal:', str(r)[:500])

# Test PRINT with alias
q4 = 'USE GRAPH HHGOA_Fraud_Graph\nCREATE OR REPLACE QUERY test_vertex6() FOR GRAPH HHGOA_Fraud_Graph {\n    Start = {Card.*};\n    Source = SELECT c FROM Start:c WHERE id(c) == "C00001-K1";\n    PRINT Source AS card;\n}'
r = conn.gsql(q4)
print('Vertex query with PRINT AS:', str(r)[:500])