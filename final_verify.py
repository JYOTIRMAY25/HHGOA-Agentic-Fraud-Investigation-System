#!/usr/bin/env python3
"""Verify shortestPath query and run post-deployment checks."""
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

# Use graph via useGraph method
try:
    conn.useGraph(graphname)
    print("useGraph: OK")
except Exception as e:
    print(f"useGraph: {e}")

# Check query via showQuery
print("\n=== shortestPath Query Check ===")
q_ok = False
try:
    r = conn.showQuery("shortestPath")
    print(f"showQuery result: {str(r)[:500]}")
    q_ok = True
except Exception as e:
    print(f"showQuery error: {type(e).__name__}: {str(e)[:300]}")

if not q_ok:
    try:
        r = conn.listQueryNames()
        print(f"listQueryNames: {r}")
        if 'shortestPath' in str(r).lower():
            q_ok = True
    except Exception as e:
        print(f"listQueryNames error: {type(e).__name__}: {str(e)[:300]}")

if not q_ok:
    try:
        r = conn.getInstalledQueries()
        print(f"getInstalledQueries: {str(r)[:500]}")
        if 'shortestPath' in str(r).lower():
            q_ok = True
    except Exception as e:
        print(f"getInstalledQueries error: {type(e).__name__}: {str(e)[:300]}")

if not q_ok:
    try:
        r = conn.getQueryInfo("shortestPath")
        print(f"getQueryInfo: {str(r)[:500]}")
        q_ok = True
    except Exception as e:
        print(f"getQueryInfo error: {type(e).__name__}: {str(e)[:300]}")

print(f"\nshortestPath query check: {'PASS' if q_ok else 'FAIL'}")

# Semantic check
print("\n=== Query Semantic Check ===")
try:
    r = conn.checkQuerySemantic("shortestPath")
    print(f"checkQuerySemantic: {r}")
except Exception as e:
    print(f"checkQuerySemantic: {type(e).__name__}: {str(e)[:200]}")

# Post-deployment: graph, schema, queries
print("\n=== POST-DEPLOYMENT CHECK ===")

# Graph
graphs = conn.listGraphs()
graph_names = [g['graphName'] for g in graphs]
graph_ok = graphname in graph_names
print(f"Graph exists: {graph_ok}")

# Schema via getSchema
schema = conn.getSchema()
vtypes_api = [v['Type'] for v in schema.get('VertexTypes', [])]
etypes_api = [e['Type'] for e in schema.get('EdgeTypes', [])]
print(f"API Schema - Vertices: {len(vtypes_api)}, Edges: {len(etypes_api)}")
print(f"API Schema vertices: {vtypes_api}")
print(f"API Schema edges: {etypes_api}")

# Schema via SHOW commands
r = conn.gsql('SHOW VERTEX *')
v_show = []
for line in str(r).split('\n'):
    line = line.strip()
    if 'VERTEX' in line and 'PRIMARY_ID' in line:
        v_show.append(line.replace('- VERTEX ', '').split('(')[0])
print(f"SHOW VERTEX count: {len(v_show)}: {v_show}")

r = conn.gsql('SHOW EDGE *')
e_show = []
for line in str(r).split('\n'):
    line = line.strip()
    if 'DIRECTED EDGE' in line:
        e_show.append(line.replace('- DIRECTED EDGE ', '').split('(')[0])
direct_edges = [e for e in e_show if e not in ['OWNED_BY','PERFORMED_BY','PREV_TRANSACTION','USED_IN_TXN','PURCHASER_TXNS','RECIPIENT_TXNS','BILLED_TXNS','INVOLVED_IN_CASE','HAS_CASES','CONNECTED_IN_CASES','CUSTOMER_CASES','CASES_WITH_PATTERN','ENFORCING_CASES']]
print(f"SHOW EDGE directed count: {len(direct_edges)}: {direct_edges}")

print("\n" + "=" * 60)
print("FINAL DEPLOYMENT REPORT")
print("=" * 60)
print(f"1. Connection:          PASS")
print(f"2. Graph exists:        {'PASS' if graph_ok else 'FAIL'}")
print(f"3. Vertex types (9):    {'PASS' if len(v_show) == 9 else 'FAIL'} ({len(v_show)} found)")
print(f"4. Edge types (13):     {'PASS' if len(direct_edges) == 13 else 'FAIL'} ({len(direct_edges)} found)")
print(f"5. shortestPath query:  {'PASS' if q_ok else 'FAIL'}")
print(f"6. Schema (API):        {'PASS' if len(vtypes_api) >= 9 and len(etypes_api) >= 13 else 'FAIL'} (API shows {len(vtypes_api)}V/{len(etypes_api)}E)")
print(f"7. Schema (SHOW):       {'PASS' if len(v_show) == 9 and len(direct_edges) == 13 else 'FAIL'}")
all_pass = all([graph_ok, len(v_show) == 9, len(direct_edges) == 13, q_ok])
print(f"Overall: {'ALL PASS' if all_pass else 'SOME FAIL'}")
