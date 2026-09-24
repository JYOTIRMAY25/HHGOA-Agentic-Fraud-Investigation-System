#!/usr/bin/env python3
import os, re
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

# Extract the query section (after "CREATE OR REPLACE QUERY shortestPath")
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
print("Deploying query from schema.gsql:")
print(query)
print()

# Drop existing query first
try:
    r = conn.gsql("DROP QUERY shortestPath")
    print("Drop: " + str(r)[:200])
except Exception as e:
    print("Drop: " + str(e)[:200])

# Deploy the query (use USE GRAPH prefix since conn.gsql doesn't persist context)
full_query = "USE GRAPH HHGOA_Fraud_Graph\n" + query
print("\nDeploying...")
try:
    r = conn.gsql(full_query)
    print("Deploy result: " + str(r)[:500])
except Exception as e:
    print("Deploy error: " + type(e).__name__ + ": " + str(e)[:500])

# Check status
print("\nChecking status...")
try:
    r = conn.getQueryInfo("shortestPath")
    res = r.get('results', [])
    if res:
        status = res[0].get('status', 'UNKNOWN')
        installed = res[0].get('installed', False)
        error = res[0].get('error', True)
        errors = res[0].get('errors', [])
        print("Status: " + status)
        print("Installed: " + str(installed))
        print("Has errors: " + str(error))
        if errors:
            print("Errors: " + str(errors)[:500])
        if status == "COMPILED" and not error:
            print("\nQuery compiled successfully! Installing...")
            try:
                r = conn.installQueries("shortestPath")
                print("Install: " + str(r)[:300])
            except Exception as e:
                print("Install error: " + type(e).__name__ + ": " + str(e)[:300])
        else:
            print("\nQuery NOT installed - compilation failed.")
    else:
        print("Query not found")
except Exception as e:
    print("Status check error: " + type(e).__name__ + ": " + str(e)[:300])
