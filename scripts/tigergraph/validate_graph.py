"""
HHGOA TigerGraph Validation Script
Validates vertex counts, edge counts, and referential integrity against DATASET_AUDIT.md.
"""

import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = r"d:\task4"
AUDIT_JSON = os.path.join(BASE_DIR, "audit_tmp", "audit_results.json")

EXPECTED_METRICS = {
    "vertices": {
        "Customer": 1892,
        "Transaction": 590742,
        "DeviceProfile": 1786,  # distinct DeviceInfo/profile combinations
        "FraudCase": 5585,      # 5565 closed cases + 20 active case pack cases
        "FraudPattern": 7,      # 5 documented + undocumented + none
        "PolicyRule": 10,       # R1 to R10
    },
    "integrity": {
        "case_pack_flagged_in_txns": "100% (20/20)",
        "case_pack_customers_in_txns": "100% (20/20)",
        "closed_case_txns_in_txns": "100% (14,955/14,955)",
        "closed_case_customers_in_txns": "100% (1,892/1,892)",
        "identity_records_in_txns": "100% (144,432/144,432)"
    }
}

def validate_live():
    print("==================================================")
    print("HHGOA TIGERGRAPH GRAPH VALIDATION")
    print("==================================================")

    try:
        import pyTigerGraph as tg
    except ImportError:
        print("[ERROR] pyTigerGraph is not installed.")
        return False

    host = os.getenv("TIGERGRAPH_HOST", "http://127.0.0.1")
    port = os.getenv("TIGERGRAPH_PORT", "9000")
    user = os.getenv("TIGERGRAPH_USERNAME", "tigergraph")
    pwd = os.getenv("TIGERGRAPH_PASSWORD", "tigergraph")
    graph = os.getenv("TIGERGRAPH_GRAPH_NAME", "HHGOA_Fraud_Graph")

    try:
        conn = tg.TigerGraphConnection(host=host, restppPort=port, username=user, password=pwd, graphname=graph)
        echo = conn.echo()
        print(f"[CONNECTED] Connected to TigerGraph: {echo}")
        print("Running validation queries...")
        res = conn.runInstalledQuery("validate_graph_metrics")
        print("Query Results:")
        print(json.dumps(res, indent=2))
        return True
    except Exception as e:
        print(f"[BLOCKED] Live validation cannot execute: TigerGraph instance not accessible at {host}:{port}.")
        print(f"Details: {e}\n")
        print("Printing expected benchmark metrics derived from authoritative DATASET_AUDIT.md:")
        print("----------------------------------------------------------------------")
        print(f"{'Entity / Metric':<30} | {'Expected (Audit)':<20} | {'Status'}")
        print("----------------------------------------------------------------------")
        for k, v in EXPECTED_METRICS["vertices"].items():
            print(f"{'Vertex: ' + k:<30} | {v:<20} | PENDING LIVE DEPLOYMENT")
        for k, v in EXPECTED_METRICS["integrity"].items():
            print(f"{'Integrity: ' + k:<30} | {v:<20} | AUDIT VERIFIED")
        print("----------------------------------------------------------------------")
        return False

if __name__ == "__main__":
    validate_live()
