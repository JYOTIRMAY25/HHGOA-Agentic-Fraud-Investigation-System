#!/usr/bin/env python3
"""Test ALTER VERTEX syntax."""
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

# Try different ALTER VERTEX syntaxes
alters = [
    "ALTER VERTEX Transaction ADD ATTRIBUTES (transaction_id STRING)",
    "ALTER VERTEX Transaction ADD ATTRIBUTES transaction_id STRING",
    "ALTER VERTEX Transaction (ADD ATTRIBUTES transaction_id STRING)",
    "ALTER VERTEX Transaction ADD transaction_id STRING",
]

for alter in alters:
    print(f"Trying: {alter}")
    try:
        r = conn.gsql(alter)
        print(f"  Result: {r}")
    except Exception as e:
        print(f"  Error: {type(e).__name__}: {str(e)[:200]}")
