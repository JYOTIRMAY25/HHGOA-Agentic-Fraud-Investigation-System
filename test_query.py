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

# Test with vertex attribute access
q2 = 'USE GRAPH HHGOA_Fraud_Graph\nCREATE OR REPLACE QUERY test_vertex() FOR GRAPH HHGOA_Fraud_Graph {\n    Start = {Card.*};\n    Source = SELECT c FROM Start:c WHERE c.card_id == "C00001-K1";\n    PRINT Source;\n}'
r = conn.gsql(q2)
print('Vertex query:', str(r)[:500])

# Now test with attribute access in ACCUM
q3 = 'USE GRAPH HHGOA_Fraud_Graph\nCREATE OR REPLACE QUERY test_vertex2() FOR GRAPH HHGOA_Fraud_Graph {\n    Start = {Card.*};\n    Source = SELECT c FROM Start:c WHERE c.card_id == "C00001-K1" ACCUM @@count += 1;\n    PRINT @@count;\n}'
r = conn.gsql(q3)
print('Vertex query 2:', str(r)[:500])