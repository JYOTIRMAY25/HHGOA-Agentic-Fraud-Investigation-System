from pyTigerGraph import TigerGraphConnection
import os

# Load env
env_vars = {}
with open('D:/task4/.env', 'r') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        if '=' in line:
            key, val = line.split('=', 1)
            env_vars[key.strip()] = val.strip()

host = env_vars.get('TG_HOST', '')
graphname = env_vars.get('TG_GRAPH', 'HHGOA_Fraud_Graph')
username = env_vars.get('TG_USERNAME', '')
password = env_vars.get('TG_PASSWORD', '')
secret = env_vars.get('TG_SECRET', '')

conn = TigerGraphConnection(
    host=host,
    graphname=graphname,
    gsqlSecret=secret,
    username=username,
    password=password,
    tgCloud=True,
)

token = conn.getToken(secret, '100000')
print('Token obtained')
conn.gsql('USE GRAPH HHGOA_Fraud_Graph')
print('Using graph HHGOA_Fraud_Graph')

# Vertex definitions
vertices = [
    'CREATE VERTEX Customer (PRIMARY_ID customer_id STRING)',
    'CREATE VERTEX Card (PRIMARY_ID card_id STRING, network STRING, card_type STRING, issuer_code STRING)',
    'CREATE VERTEX Transaction (PRIMARY_ID transaction_id STRING, ts DATETIME, amount FLOAT, channel STRING, product_cd STRING, risk_score FLOAT, dist1 FLOAT, dist2 FLOAT, is_flagged BOOL DEFAULT false)',
    'CREATE VERTEX DeviceProfile (PRIMARY_ID device_profile_id STRING, device_info STRING, device_type STRING, os STRING, browser STRING, screen_resolution STRING, device_status STRING, proxy_flag STRING, match_status STRING)',
    'CREATE VERTEX EmailDomain (PRIMARY_ID domain_name STRING)',
    'CREATE VERTEX BillingRegion (PRIMARY_ID region_id STRING, region_code STRING, country_code STRING, is_domestic BOOL DEFAULT true)',
    'CREATE VERTEX FraudCase (PRIMARY_ID case_id STRING, status STRING, trigger_type STRING, trigger_text STRING, opened_at DATETIME, closed_at DATETIME, outcome STRING, pattern STRING, exposure_usd FLOAT DEFAULT 0.0, report_filed BOOL DEFAULT false, actions_taken STRING, approval_route STRING, analyst_notes STRING, sar_narrative STRING)',
    'CREATE VERTEX FraudPattern (PRIMARY_ID pattern_id STRING, pattern_name STRING, description STRING, typology_rules STRING)',
    'CREATE VERTEX PolicyRule (PRIMARY_ID rule_id STRING, rule_name STRING, description STRING, condition STRING, prescribed_action STRING, approval_route STRING)',
]

for v in vertices:
    try:
        result = conn.gsql(v)
        print(f'OK: {v[:60]}...')
    except Exception as e:
        print(f'FAIL: {v[:60]}... - {e}')

# Edge definitions
edges = [
    'CREATE DIRECTED EDGE OWNS (FROM Customer, TO Card, opened_date DATETIME) WITH REVERSE_EDGE="OWNED_BY"',
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

for e in edges:
    try:
        result = conn.gsql(e)
        print(f'OK: {e[:60]}...')
    except Exception as ex:
        print(f'FAIL: {e[:60]}... - {ex}')

print('Schema creation complete!')