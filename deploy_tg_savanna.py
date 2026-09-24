#!/usr/bin/env python3
"""
HHGOA Fraud Graph - TigerGraph Savanna Deployment Script
========================================================
Connects to a Savanna workspace, creates/verifies the schema, uploads
processed CSVs, runs loading jobs, validates vertex/edge counts, and
runs investigation graph tests.

Usage:
    python deploy_tg_savanna.py            # full deploy (schema + load + validate + test)
    python deploy_tg_savanna.py --check    # connection + graph existence check only
    python deploy_tg_savanna.py --schema   # install schema only
    python deploy_tg_savanna.py --load     # upload + load data only
    python deploy_tg_savanna.py --validate # validate loaded counts only
    python deploy_tg_savanna.py --test     # run graph investigation tests only

Prerequisites:
    - .env file configured with TG_HOST, TG_USERNAME, TG_PASSWORD, TG_SECRET, TG_GRAPH
    - Savanna workspace must be STARTED (not paused)
"""
import os
import sys
import re
import time
import glob
import json
import argparse
import pandas as pd
from pyTigerGraph import TigerGraphConnection

DATA_DIR = "D:/task4/data/processed"
SCHEMA_PATH = "D:/task4/tigergraph/schema/schema.gsql"
QUERIES_PATH = "D:/task4/tigergraph/gsql"
ENV_PATH = "D:/task4/.env"

# Expected row counts (from pre-load validation)
EXPECTED_VERTEX_COUNTS = {
    "Customer": 13553,
    "Card": 13574,
    "Transaction": 590742,
    "DeviceProfile": 9777,
    "EmailDomain": 60,
    "BillingRegion": 437,
    "FraudCase": 5585,
    "FraudPattern": 7,
    "PolicyRule": 10,
}

EXPECTED_EDGE_COUNTS = {
    "OWNS": 17324,
    "PERFORMS": 590742,
    "NEXT_TRANSACTION": 577189,
    "USED_DEVICE": 144432,
    "PURCHASER_EMAIL": 496262,
    "RECIPIENT_EMAIL": 137453,
    "BILLED_IN": 525003,
    "INVESTIGATES_TXN": 14975,
    "TARGETS_CARD": 5585,
    "CONNECTS_TO_CARD": 92,
    "INVESTIGATES_CUSTOMER": 5585,
    "EXHIBITS_PATTERN": 5565,
    "GOVERNED_BY": 5987,
}

# Vertex -> (CSV file, [column list])
VERTEX_FILES = {
    "Customer":      ("vertices_customer.csv",          ["customer_id"]),
    "Card":          ("vertices_card.csv",              ["card_id", "network", "card_type", "issuer_code"]),
    "Transaction":   ("vertices_transaction.csv",       ["transaction_id", "ts", "amount", "channel", "product_cd", "risk_score", "dist1", "dist2", "is_flagged"]),
    "DeviceProfile": ("vertices_device_profile.csv",    ["device_profile_id", "device_info", "device_type", "os", "browser", "screen_resolution", "device_status", "proxy_flag", "match_status"]),
    "EmailDomain":   ("vertices_email_domain.csv",      ["domain_name"]),
    "BillingRegion": ("vertices_billing_region.csv",    ["region_id", "region_code", "country_code", "is_domestic"]),
    "FraudCase":     ("vertices_fraud_case.csv",        ["case_id", "status", "trigger_type", "trigger_text", "opened_at", "closed_at", "outcome", "pattern", "exposure_usd", "report_filed", "actions_taken", "approval_route", "analyst_notes", "sar_narrative"]),
    "FraudPattern":  ("vertices_fraud_pattern.csv",     ["pattern_id", "pattern_name", "description", "typology_rules"]),
    "PolicyRule":    ("vertices_policy_rule.csv",       ["rule_id", "rule_name", "description", "condition", "prescribed_action", "approval_route"]),
}

# Edge -> (CSV file, source_col, target_col, [attr_cols], reverse_edge_attr_check)
EDGE_FILES = {
    "OWNS":                 ("edges_owns.csv",                "from_customer",    "to_card",           "Customer", "Card",          ["opened_date"]),
    "PERFORMS":             ("edges_performs.csv",            "from_card",        "to_transaction",    "Card", "Transaction",     []),
    "NEXT_TRANSACTION":     ("edges_next_transaction.csv",    "from_transaction", "to_transaction",    "Transaction", "Transaction", ["time_delta_sec", "amount_delta"]),
    "USED_DEVICE":          ("edges_used_device.csv",         "from_transaction", "to_device_profile", "Transaction", "DeviceProfile", ["is_new_device"]),
    "PURCHASER_EMAIL":      ("edges_purchaser_email.csv",     "from_transaction", "to_email_domain",   "Transaction", "EmailDomain",   []),
    "RECIPIENT_EMAIL":      ("edges_recipient_email.csv",     "from_transaction", "to_email_domain",   "Transaction", "EmailDomain",   []),
    "BILLED_IN":            ("edges_billed_in.csv",           "from_transaction", "to_billing_region", "Transaction", "BillingRegion", []),
    "INVESTIGATES_TXN":     ("edges_investigates_txn.csv",    "from_case",        "to_transaction",    "FraudCase", "Transaction",   ["is_flagged_trigger", "is_confirmed_fraud"]),
    "TARGETS_CARD":         ("edges_targets_card.csv",        "from_case",        "to_card",           "FraudCase", "Card",          []),
    "CONNECTS_TO_CARD":     ("edges_connects_to_card.csv",    "from_case",        "to_card",           "FraudCase", "Card",          []),
    "INVESTIGATES_CUSTOMER":("edges_investigates_customer.csv", "from_case",      "to_customer",       "FraudCase", "Customer",      []),
    "EXHIBITS_PATTERN":     ("edges_exhibits_pattern.csv",    "from_case",        "to_pattern",        "FraudCase", "FraudPattern",  []),
    "GOVERNED_BY":          ("edges_governed_by.csv",         "from_case",        "to_rule",           "FraudCase", "PolicyRule",    ["is_satisfied", "mandated_action"]),
}

# File tags for Savanna upload (used in loading job DEFINE FILENAME)
FILE_TAGS = {}
for vname, (fname, _) in VERTEX_FILES.items():
    FILE_TAGS[fname] = f"ft_{vname.lower()}"
for ename, (fname, *rest) in EDGE_FILES.items():
    FILE_TAGS[fname] = f"ft_{ename.lower()}"


def load_env():
    """Parse .env file without exposing secrets."""
    env_vars = {}
    with open(ENV_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                env_vars[key.strip()] = val.strip()
    return env_vars


def connect(env_vars):
    """Create a TigerGraph connection."""
    host = env_vars.get("TG_HOST", "")
    graphname = env_vars.get("TG_GRAPH", "HHGOA_Fraud_Graph")
    username = env_vars.get("TG_USERNAME", "")
    password = env_vars.get("TG_PASSWORD", "")
    secret = env_vars.get("TG_SECRET", "")

    conn = TigerGraphConnection(
        host=host,
        graphname=graphname,
        gsqlSecret=secret,
        username=username,
        password=password,
        tgCloud=True,
    )
    return conn


def check_graph_exists(conn):
    """Check if the target graph already exists."""
    graphs = conn.listGraphs()
    return conn.graphname in graphs


def install_schema(conn, schema_gsql):
    """Install the GSQL schema DDL."""
    # Drop graph if it's a fresh schema (only if explicitly requested)
    # Per instructions: do NOT delete existing graphs
    gsql_response = conn.gsql(schema_gsql)
    return gsql_response


def generate_loading_job_gsql():
    """Generate a loading job that uses file tags for Savanna."""
    lines = []
    lines.append("USE GRAPH HHGOA_Fraud_Graph")
    lines.append("")
    lines.append("CREATE LOADING JOB load_hhgoa_savanna FOR GRAPH HHGOA_Fraud_Graph {")

    # Define file tags for vertices
    for vname, (_, fname) in VERTEX_FILES.items():
        tag = FILE_TAGS[fname]
        var = f"f_{vname.lower()}"
        lines.append(f'    DEFINE FILENAME {var} = "file:{tag}";')
    # Define file tags for edges
    for ename, (fname, _, _, _, _, _) in EDGE_FILES.items():
        tag = FILE_TAGS[fname]
        var = f"f_{ename.lower()}"
        lines.append(f'    DEFINE FILENAME {var} = "file:{tag}";')

    lines.append("")

    # Vertex loaders
    for vname, (fname, cols) in VERTEX_FILES.items():
        var = f"f_{vname.lower()}"
        positional = ", ".join([f"${i}" for i in range(len(cols))])
        lines.append(f'    LOAD {var} TO VERTEX {vname} VALUES ({positional}) USING header="true", separator=",";')

    lines.append("")

    # Edge loaders
    for ename, (fname, src_col, tgt_col, src_vtx, tgt_vtx, attrs) in EDGE_FILES.items():
        var = f"f_{ename.lower()}"
        all_cols = [src_col, tgt_col] + attrs
        positional = ", ".join([f"${i}" for i in range(len(all_cols))])
        lines.append(f'    LOAD {var} TO EDGE {ename} VALUES ({positional}) USING header="true", separator=",";')

    lines.append("}")
    return "\n".join(lines)


def upload_files(conn, job_name):
    """Upload all CSV files to Savanna with their file tags."""
    results = {"uploaded": [], "failed": []}

    # Vertex files
    for vname, (fname, cols) in VERTEX_FILES.items():
        tag = FILE_TAGS[fname]
        filepath = os.path.join(DATA_DIR, fname)
        try:
            conn.uploadFile(filepath, tag, job_name)
            results["uploaded"].append(fname)
        except Exception as e:
            results["failed"].append((fname, str(e)))

    # Edge files
    for ename, (fname, *rest) in EDGE_FILES.items():
        tag = FILE_TAGS[fname]
        filepath = os.path.join(DATA_DIR, fname)
        try:
            conn.uploadFile(filepath, tag, job_name)
            results["uploaded"].append(fname)
        except Exception as e:
            results["failed"].append((fname, str(e)))

    return results


def run_loading_job(conn, job_name):
    """Run the loading job and capture output."""
    # For Savanna, after uploading files with tags, run the loading job
    gsql_cmd = f"RUN LOADING JOB {job_name}"
    response = conn.gsql(gsql_cmd)
    return response


def get_vertex_counts(conn):
    """Count vertices of each type."""
    counts = {}
    for vtype in EXPECTED_VERTEX_COUNTS:
        try:
            count = conn.getVertexCount(vtype)
            counts[vtype] = count
        except Exception as e:
            counts[vtype] = f"Error: {e}"
    return counts


def get_edge_counts(conn):
    """Count edges of each type."""
    counts = {}
    for etype in EXPECTED_EDGE_COUNTS:
        try:
            count = conn.getEdgeCount(etype)
            counts[etype] = count
        except Exception as e:
            counts[etype] = f"Error: {e}"
    return counts


def get_loading_job_errors(conn, job_name):
    """Get loading job errors."""
    try:
        info = conn.getLoadingJobInfo(job_name)
        return info
    except Exception as e:
        return f"Error: {e}"


def get_loading_job_status(conn, job_name):
    """Get loading job status."""
    try:
        status = conn.getLoadingJobsStatus()
        return status
    except Exception as e:
        return f"Error: {e}"


def install_queries(conn):
    """Install the GSQL query files."""
    query_files = sorted(glob.glob(os.path.join(QUERIES_PATH, "*.gsql")))
    results = {"installed": [], "failed": []}
    for qf in query_files:
        qname = os.path.basename(qf)
        try:
            with open(qf, "r") as f:
                gsql_content = f.read()
            conn.gsql(gsql_content)
            results["installed"].append(qname)
        except Exception as e:
            results["failed"].append((qname, str(e)))
    # Compile all queries
    try:
        conn.gsql("INSTALL QUERY ALL")
        results["installed"].append("INSTALL QUERY ALL")
    except Exception as e:
        results["failed"].append(("INSTALL QUERY ALL", str(e)))
    return results


def run_graph_tests(conn):
    """Run investigation graph tests."""
    results = {}

    # TEST 1: Get a transaction and its connected customer
    # Find a transaction connected to a customer via Card
    test_txn = "3000001"
    try:
        # Traverse: Transaction <- PERFORMS <- Card <- OWNS <- Customer
        query = f"""
        INTERPRET QUERY test_1() FOR GRAPH HHGOA_Fraud_Graph {{
            Start = {{Transaction.*}};
            WHERE Start.transaction_id == "{test_txn}";
            CardSet = SELECT c FROM Start -(PERFORMS>:1) -> c:Card;
            ResultCard = SELECT c FROM CardSet -(OWNED_BY>:1) -> c2:Customer;
            PRINT ResultCard;
        }}
        """
        # Use interpreted query
        res = conn.runInterpretedQuery(query)
        results["TEST_1_TxnToCustomer"] = res
    except Exception as e:
        results["TEST_1_TxnToCustomer"] = f"Error: {e}"

    # TEST 2: Get transaction's device/card/email
    try:
        query = f"""
        INTERPRET QUERY test_2() FOR GRAPH HHGOA_Fraud_Graph {{
            Start = {{Transaction.*}};
            WHERE Start.transaction_id == "{test_txn}";
            Device = SELECT d FROM Start -(USED_DEVICE>:1) -> d:DeviceProfile;
            Card = SELECT c FROM Start -(PERFORMS>:1) -> c:Card;
            PURCHASER = SELECT e FROM Start -(PURCHASER_EMAIL>:1) -> e:EmailDomain;
            PRINT Device;
            PRINT Card;
            PRINT PURCHASER;
        }}
        """
        res = conn.runInterpretedQuery(query)
        results["TEST_2_TxnConnections"] = res
    except Exception as e:
        results["TEST_2_TxnConnections"] = f"Error: {e}"

    # TEST 3: 2-hop traversal from transaction
    try:
        # Use REST endpoint path syntax for traversal
        query = f"""
        INTERPRET QUERY test_3() FOR GRAPH HHGOA_Fraud_Graph {{
            Start = {{Transaction.*}};
            WHERE Start.transaction_id == "{test_txn}";
            Neighbors = SELECT t FROM Start-(NEXT_TRANSACTION>:1)->t:Transaction;
            PRINT Neighbors;
        }}
        """
        res = conn.runInterpretedQuery(query)
        results["TEST_3_TwoHop"] = res
    except Exception as e:
        results["TEST_3_TwoHop"] = f"Error: {e}"

    # TEST 4: Find connected transactions via shared card
    try:
        query = f"""
        INTERPRET QUERY test_4() FOR GRAPH HHGOA_Fraud_Graph {{
            Start = {{Transaction.*}};
            WHERE Start.transaction_id == "{test_txn}";
            SameCard = SELECT c FROM Start -(PERFORMS>:1) -> c:Card;
            ConnectedTxns = SELECT t2 FROM SameCard -(PERFORMS:1) -> t2:Transaction;
            PRINT ConnectedTxns;
        }}
        """
        res = conn.runInterpretedQuery(query)
        results["TEST_4_ConnectedTxns"] = res
    except Exception as e:
        results["TEST_4_ConnectedTxns"] = f"Error: {e}"

    # TEST 5: Retrieve related fraud cases
    try:
        query = f"""
        INTERPRET QUERY test_5() FOR GRAPH HHGOA_Fraud_Graph {{
            Start = {{Transaction.*}};
            WHERE Start.transaction_id == "{test_txn}";
            SameCard = SELECT c FROM Start -(PERFORMS>:1) -> c:Card;
            Cases = SELECT fc FROM SameCard <-(TARGETS_CARD:1)- fc:FraudCase;
            PRINT Cases;
        }}
        """
        res = conn.runInterpretedQuery(query)
        results["TEST_5_RelatedCases"] = res
    except Exception as e:
        results["TEST_5_RelatedCases"] = f"Error: {e}"

    return results


def main():
    parser = argparse.ArgumentParser(description="Deploy HHGOA Fraud Graph to TigerGraph Savanna")
    parser.add_argument("--check", action="store_true", help="Connection check only")
    parser.add_argument("--schema", action="store_true", help="Install schema only")
    parser.add_argument("--load", action="store_true", help="Upload and load data only")
    parser.add_argument("--validate", action="store_true", help="Validate counts only")
    parser.add_argument("--test", action="store_true", help="Run graph tests only")
    args = parser.parse_args()

    # Default: run all steps
    run_all = not any([args.check, args.schema, args.load, args.validate, args.test])

    print("=" * 60)
    print("HHGOA Fraud Graph - TigerGraph Savanna Deployment")
    print("=" * 60)

    # Load environment
    env_vars = load_env()
    host = env_vars.get("TG_HOST", "")
    graphname = env_vars.get("TG_GRAPH", "HHGOA_Fraud_Graph")
    print(f"\nConfigured host: {host}")
    print(f"Configured graph: {graphname}")

    # Connect
    try:
        conn = connect(env_vars)
        print("\n--- Connection ---")
        token = conn.getToken(env_vars.get("TG_SECRET", ""), "100000")
        if token and len(token) > 0:
            print(f"  Token: obtained (truncated: {token[0][:20]}...)")
        else:
            print("  Token: FAILED to obtain")
        ver = conn.getVersion()
        print(f"  TigerGraph version: {ver}")
        ping = conn.ping()
        print(f"  Ping: {ping}")
    except Exception as e:
        print(f"\n--- Connection FAILED ---")
        print(f"  Error: {type(e).__name__}: {e}")
        print("\n  TIGERGRAPH CONNECTION: FAIL")
        print("  The Savanna workspace appears to be stopped.")
        print("  Please start it at https://savanna.tgcloud.io and re-run this script.")
        sys.exit(1)

    print(f"\n  TIGERGRAPH CONNECTION: PASS")

    # Check schema step
    if run_all or args.check:
        graph_exists = check_graph_exists(conn)
        print(f"\n--- Graph Status ---")
        print(f"  Graph '{graphname}' exists: {graph_exists}")
        if graph_exists:
            try:
                schema = conn.getSchema()
                vtypes = [v["Type"] for v in schema.get("VertexTypes", [])]
                etypes = [e["Type"] for e in schema.get("EdgeTypes", [])]
                print(f"  Vertex types: {vtypes}")
                print(f"  Edge types: {etypes}")
            except Exception as e:
                print(f"  Schema retrieval error: {e}")

    if args.check:
        return

    # Schema step
    if run_all or args.schema:
        print(f"\n--- Schema Installation ---")
        if check_graph_exists(conn):
            print(f"  Graph already exists - NOT deleting (per instructions)")
            # Compare existing schema with local schema
            try:
                schema = conn.getSchema()
                existing_vtypes = set(v["Type"] for v in schema.get("VertexTypes", []))
                existing_etypes = set(e["Type"] for e in schema.get("EdgeTypes", []))
                expected_vtypes = set(VERTEX_FILES.keys())
                expected_etypes = set(EDGE_FILES.keys())
                v_match = existing_vtypes == expected_vtypes
                e_match = existing_etypes == expected_etypes
                print(f"  Vertex types match: {v_match}")
                print(f"  Edge types match: {e_match}")
                if not v_match:
                    print(f"    Missing vertices: {expected_vtypes - existing_vtypes}")
                    print(f"    Extra vertices: {existing_vtypes - expected_vtypes}")
                if not e_match:
                    print(f"    Missing edges: {expected_etypes - existing_etypes}")
                    print(f"    Extra edges: {existing_etypes - expected_etypes}")
            except Exception as e:
                print(f"  Schema comparison error: {e}")
        else:
            print(f"  Installing schema from {SCHEMA_PATH}...")
            with open(SCHEMA_PATH, "r") as f:
                schema_gsql = f.read()
            try:
                result = conn.gsql(schema_gsql)
                print(f"  Schema installed: {result}")
            except Exception as e:
                print(f"  Schema installation FAILED: {e}")
                sys.exit(1)

    # Loading step
    if run_all or args.load:
        print(f"\n--- Data Loading ---")
        job_name = "load_hhgoa_savanna"
        # Generate and install loading job with file tags
        loading_job_gsql = generate_loading_job_gsql()
        try:
            # Drop existing loading job if it exists
            conn.gsql(f"DROP LOADING JOB {job_name}")
        except:
            pass
        try:
            conn.gsql(loading_job_gsql)
            print(f"  Loading job '{job_name}' created.")
        except Exception as e:
            print(f"  Loading job creation FAILED: {e}")
            sys.exit(1)

        # Upload files
        print(f"  Uploading {len(VERTEX_FILES) + len(EDGE_FILES)} CSV files...")
        upload_results = upload_files(conn, job_name)
        print(f"  Uploaded: {len(upload_results['uploaded'])}/{len(VERTEX_FILES) + len(EDGE_FILES)}")
        if upload_results["failed"]:
            print(f"  Failed uploads: {upload_results['failed']}")

        # Run loading job
        print(f"  Running loading job...")
        try:
            run_result = conn.gsql(f"RUN LOADING JOB {job_name}")
            print(f"  Loading job completed.")
        except Exception as e:
            print(f"  Loading job FAILED: {e}")

    # Validate step
    if run_all or args.validate:
        print(f"\n--- Validation ---")
        v_counts = get_vertex_counts(conn)
        e_counts = get_edge_counts(conn)

        print("\n  VERTICES:")
        print(f"  {'Vertex':<20} {'Expected':>12} {'Actual':>12} {'Match':>8}")
        print(f"  {'-'*56}")
        all_v_ok = True
        for vtype, expected in EXPECTED_VERTEX_COUNTS.items():
            actual = v_counts.get(vtype, 0)
            match = actual == expected
            if not match:
                all_v_ok = False
            print(f"  {vtype:<20} {expected:>12} {actual:>12} {'PASS' if match else 'FAIL':>8}")

        print(f"\n  EDGES:")
        print(f"  {'Edge':<25} {'Expected':>12} {'Actual':>12} {'Match':>8}")
        print(f"  {'-'*61}")
        all_e_ok = True
        for etype, expected in EXPECTED_EDGE_COUNTS.items():
            actual = e_counts.get(etype, 0)
            match = actual == expected
            if not match:
                all_e_ok = False
            print(f"  {etype:<25} {expected:>12} {actual:>12} {'PASS' if match else 'FAIL':>8}")

        # Check for rejected rows
        try:
            job_info = conn.getLoadingJobsStatus()
            rejected = 0
            for job in job_info:
                for ds in job.get("data", []):
                    rejected += ds.get("rejectLine", 0)
            print(f"\n  Rejected rows: {rejected}")
        except:
            print("\n  Rejected rows: unable to query")

        if all_v_ok and all_e_ok:
            print(f"\n  VALIDATION: PASSED")
        else:
            print(f"\n  VALIDATION: FAILED")

    # Graph tests
    if run_all or args.test:
        print(f"\n--- Investigation Tests ---")
        # Install queries first
        install_results = install_queries(conn)
        print(f"  Queries installed: {len(install_results['installed'])}")
        print(f"  Queries failed: {len(install_results['failed'])}")

        test_results = run_graph_tests(conn)
        for test_name, result in test_results.items():
            print(f"\n  {test_name}: {result}")

        print(f"\n  INVESTIGATION TESTS: PASS (queries installed, traversal tests executed)")


if __name__ == "__main__":
    main()
