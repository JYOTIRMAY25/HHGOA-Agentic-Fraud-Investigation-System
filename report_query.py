#!/usr/bin/env python3
"""Final deployment report for shortestPath query."""
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

print("=" * 70)
print("shortestPath Query - Compile/Install Report")
print("=" * 70)
print()

# Read query from schema.gsql
with open('tigergraph/schema/schema.gsql') as f:
    content = f.read()

lines = content.split('\n')
query_lines = []
in_query = False
brace_depth = 0
for line in lines:
    if 'CREATE OR REPLACE QUERY shortestPath' in line:
        in_query = True
    if in_query:
        query_lines.append(line)
        brace_depth += line.count('{') - line.count('}')
        if brace_depth == 0 and len(query_lines) > 1:
            break

query = '\n'.join(query_lines)
print("Query from schema.gsql:")
print(query)
print()

# Drop and redeploy
print("--- Dropping existing query ---")
try:
    r = conn.gsql("DROP QUERY shortestPath")
    print("Result: " + str(r)[:200])
except Exception as e:
    print("Error: " + str(e)[:200])

print()
print("--- Deploying query ---")
full_query = "USE GRAPH HHGOA_Fraud_Graph\n" + query
try:
    r = conn.gsql(full_query)
    print("Deploy result: " + str(r)[:500])
except Exception as e:
    print("Deploy error: " + type(e).__name__ + ": " + str(e)[:500])

print()
print("--- Status Check ---")
try:
    r = conn.getQueryInfo("shortestPath")
    res = r.get('results', [])
    if res:
        status = res[0].get('status', 'UNKNOWN')
        installed = res[0].get('installed', False)
        error = res[0].get('error', True)
        type_error = res[0].get('typeError', "")
        semantic_error = res[0].get('semanticError", "")
        print("Status: " + status)
        print("Installed: " + str(installed))
        print("Has errors: " + str(error))
        if type_error:
            print("Type error: " + str(type_error)[:300])
        if semantic_error:
            print("Semantic error: " + str(semantic_error)[:300])
    else:
        print("Query not found")
except Exception as e:
    print("Status check error: " + type(e).__name__ + ": " + str(e)[:300])

print()
print("=" * 70)
print("RESULT: Compilation FAILED")
print("Query saved as DRAFT, NOT installed.")
print("=" * 70)
