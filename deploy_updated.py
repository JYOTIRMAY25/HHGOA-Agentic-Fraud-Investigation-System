#!/usr/bin/env python3
"""Deploy updated shortestPath query."""
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

# Read updated query from schema.gsql
with open('tigergraph/schema/schema.gsql') as f:
    content = f.read()

# Extract just the query part
import re
content_no_comments = re.sub(r'//.*', '', content)
# Find the shortestPath query
match = re.search(r'(CREATE OR REPLACE QUERY shortestPath.*?^})', content_no_comments, re.MULTILINE | re.DOTALL)
if match:
    query = match.group(1)
    print("Deploying query:")
    print(query[:200])
    print("...")
    try:
        r = conn.gsql(query)
        print("Result:", str(r)[:500])
    except Exception as e:
        print("Error:", type(e).__name__, str(e)[:500])
else:
    print("Could not find query in schema file")
