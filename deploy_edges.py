#!/usr/bin/env python3
"""Deploy missing edges with delays."""
import os, time
from dotenv import load_dotenv
load_dotenv('D:/task4/.env')
from pyTigerGraph import TigerGraphConnection

host = os.getenv('TG_HOST')
graphname = os.getenv('TG_GRAPH')
username = os.getenv('TG_USERNAME')
password = os.getenv('TG_PASSWORD')
secret = os.getenv('TG_SECRET')

conn = TigerGraphConnection(host=host, graphname=graphname, gsqlSecret=secret, username=username, password=password, tgCloud=True, sslPort=443)

edges = [
    'CREATE DIRECTED EDGE PERFORMS (FROM Card, TO Transaction) WITH REVERSE_EDGE="PERFORMED_BY"',
    'CREATE DIRECTED EDGE NEXT_TRANSACTION (FROM Transaction, TO Transaction, time_delta_sec INT, amount_delta FLOAT) WITH REVERSE_EDGE="PREV_TRANSACTION"',
    'CREATE DIRECTED EDGE USED_DEVICE (FROM Transaction, TO DeviceProfile, is_new_device BOOL) WITH REVERSE_EDGE="USED_IN_TXN"',
    'CREATE DIRECTED EDGE PURCHASER_EMAIL (FROM Transaction, TO EmailDomain) WITH REVERSE_EDGE="PURCHASER_TXNS"',
    'CREATE DIRECTED EDGE RECIPIENT_EMAIL (FROM Transaction, TO EmailDomain) WITH REVERSE_EDGE="RECIPIENT_TXNS"',
    'CREATE DIRECTED EDGE BILLED_IN (FROM Transaction, TO BillingRegion) WITH REVERSE_EDGE="BILLED_TXNS"',
    'CREATE DIRECTED EDGE INVESTIGATES_TXN (FROM FraudCase, TO Transaction, is_flagged_trigger BOOL, is_confirmed_fraud BOOL) WITH REVERSE_EDGE="INVOLVED_IN_CASE"',
    'CREATE DIRECTED EDGE TARGETS_CARD (FROM FraudCase, TO Card) WITH REVERSE_EDGE="HAS_CASES"',
    'CREATE DIRECTED EDGE CONNECTS_TO_CARD (FROM FraudCase, TO Card) WITH REVERSE_EDGE="CONNECTED_IN_CASES"',
    'CREATE DIRECTED EDGE INVESTIGATES_CUSTOMER (FROM FraudCase, TO Customer) WITH REVERSE_EDGE="CUSTOMER_CASES"',
    'CREATE DIRECTED EDGE EXHIBITS_PATTERN (FROM FraudCase, TO FraudPattern) WITH REVERSE_EDGE="CASES_WITH_PATTERN"',
    'CREATE DIRECTED EDGE GOVERNED_BY (FROM FraudCase, TO PolicyRule, is_satisfied BOOL, mandated_action STRING) WITH REVERSE_EDGE="ENFORCING_CASES"',
]

for i, edge in enumerate(edges):
    try:
        r = conn.gsql(edge)
        print(f"[{i+1}/{len(edges)}] PASS: {edge[:60]}")
    except Exception as e:
        print(f"[{i+1}/{len(edges)}] FAIL: {edge[:60]} -> {str(e)[:150]}")
    time.sleep(1)

# Verify
print("\n--- Verification ---")
try:
    r = conn.gsql('SHOW EDGE *')
    print(str(r)[:3000])
except Exception as e:
    print('Error:', e)
