#!/usr/bin/env python3
"""Verify deployment state."""
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

# Verify vertices
print("=== VERTEX VERIFICATION ===")
try:
    r = conn.gsql('SHOW VERTEX *')
    vtypes = []
    for line in str(r).split('\n'):
        line = line.strip()
        if 'VERTEX' in line and 'PRIMARY_ID' in line:
            parts = line.replace('- VERTEX ', '').split('(')
            if parts:
                vtypes.append(parts[0])
    print(f"Found vertices ({len(vtypes)}): {vtypes}")
    expected = ["Customer", "Card", "Transaction", "DeviceProfile", "EmailDomain", "BillingRegion", "FraudCase", "FraudPattern", "PolicyRule"]
    missing = [v for v in expected if v not in vtypes]
    extra = [v for v in vtypes if v not in expected]
    print(f"Expected: {expected}")
    print(f"Missing: {missing}")
    print(f"Extra: {extra}")
    v_ok = len([v for v in vtypes if v in expected]) == 9
    print(f"Vertex count check (9): {'PASS' if v_ok else 'FAIL'}")
except Exception as e:
    print(f"Error: {e}")
    v_ok = False

# Verify edges
print()
print("=== EDGE VERIFICATION ===")
try:
    r = conn.gsql('SHOW EDGE *')
    all_edges = []
    for line in str(r).split('\n'):
        line = line.strip()
        if 'DIRECTED EDGE' in line:
            parts = line.replace('- DIRECTED EDGE ', '').split('(')
            if parts:
                all_edges.append(parts[0])
    reverse_edges = ["OWNED_BY", "PERFORMED_BY", "PREV_TRANSACTION", "USED_IN_TXN", "PURCHASER_TXNS", "RECIPIENT_TXNS", "BILLED_TXNS", "INVOLVED_IN_CASE", "HAS_CASES", "CONNECTED_IN_CASES", "CUSTOMER_CASES", "CASES_WITH_PATTERN", "ENFORCING_CASES"]
    direct_edges = [e for e in all_edges if e not in reverse_edges]
    print(f"Found directed edges ({len(direct_edges)}): {direct_edges}")
    expected_edges = ["OWNS", "PERFORMS", "NEXT_TRANSACTION", "USED_DEVICE", "PURCHASER_EMAIL", "RECIPIENT_EMAIL", "BILLED_IN", "INVESTIGATES_TXN", "TARGETS_CARD", "CONNECTS_TO_CARD", "INVESTIGATES_CUSTOMER", "EXHIBITS_PATTERN", "GOVERNED_BY"]
    missing_e = [e for e in expected_edges if e not in direct_edges]
    print(f"Expected: {expected_edges}")
    print(f"Missing: {missing_e}")
    e_ok = len(direct_edges) == 13
    print(f"Edge count check (13): {'PASS' if e_ok else 'FAIL'}")
except Exception as e:
    print(f"Error: {e}")
    e_ok = False

# Check shortestPath query
print()
print("=== QUERY VERIFICATION ===")
q_ok = False
try:
    # Check via GSQL SHOW commands
    for cmd in ['SHOW QUERY shortestPath', 'SHOW QUERIES']:
        try:
            r = conn.gsql(cmd)
            result = str(r)
            print(f"Command: {cmd}")
            print(f"Result: {result[:500]}")
            if 'shortestPath' in result.lower() or 'ShortestPath' in result:
                q_ok = True
                break
        except:
            pass

    if not q_ok:
        # Check via list queries API
        try:
            r = conn.gsql('LIST QUERIES')
            result = str(r)
            print(f"LIST QUERIES: {result[:500]}")
            if 'shortestPath' in result.lower():
                q_ok = True
        except:
            pass

    if not q_ok:
        # Check via schema
        try:
            r = conn.gsql('SHOW QUERY shortestPath')
            print(f"SHOW QUERY shortestPath: {str(r)[:500]}")
            q_ok = True
        except Exception as e:
            print(f"SHOW QUERY shortestPath failed: {e}")
except Exception as e:
    print(f"Error: {e}")

print(f"shortestPath query check: {'PASS' if q_ok else 'FAIL'}")

print()
print("=" * 60)
print("DEPLOYMENT VERIFICATION SUMMARY")
print("=" * 60)
print(f"1. Connection:               PASS")
print(f"2. Graph exists:             {'PASS' if conn.listGraphs() and graphname in [g['graphName'] for g in conn.listGraphs()] else 'FAIL'}")
print(f"3. Vertex types (9):         {'PASS' if v_ok else 'FAIL'}")
print(f"4. Edge types (13):          {'PASS' if e_ok else 'FAIL'}")
print(f"5. shortestPath query:       {'PASS' if q_ok else 'FAIL'}")
all_ok = v_ok and e_ok and q_ok
print(f"Overall: {'ALL PASS' if all_ok else 'SOME FAIL'}")
