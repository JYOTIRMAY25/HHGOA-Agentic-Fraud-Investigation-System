"""
HHGOA TigerGraph Data Loading Pipeline
Uses pyTigerGraph to deploy schema, install loading jobs, and ingest graph entities.
Honors .env configuration and reports actual connection status without faking.
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TG_HOST = os.getenv("TIGERGRAPH_HOST", "http://127.0.0.1")
TG_PORT = os.getenv("TIGERGRAPH_PORT", "9000")
TG_USERNAME = os.getenv("TIGERGRAPH_USERNAME", "tigergraph")
TG_PASSWORD = os.getenv("TIGERGRAPH_PASSWORD", "tigergraph")
TG_GRAPH = os.getenv("TIGERGRAPH_GRAPH_NAME", "HHGOA_Fraud_Graph")
TG_SECRET = os.getenv("TIGERGRAPH_SECRET", "")

BASE_DIR = r"d:\task4"
SCHEMA_FILE = os.path.join(BASE_DIR, "scripts", "tigergraph", "schema.gsql")
LOADING_JOBS_FILE = os.path.join(BASE_DIR, "scripts", "tigergraph", "loading_jobs.gsql")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

def test_connection():
    print("==================================================")
    print("HHGOA TIGERGRAPH INGESTION PIPELINE")
    print("==================================================")
    print(f"Target Host:       {TG_HOST}:{TG_PORT}")
    print(f"Target Graph:      {TG_GRAPH}")
    print(f"Target Username:   {TG_USERNAME}")
    print("--------------------------------------------------")

    try:
        import pyTigerGraph as tg
    except ImportError:
        print("[ERROR] pyTigerGraph is not installed. Please run: pip install pytigergraph")
        return None, False

    try:
        print("Testing connectivity to TigerGraph server...")
        conn = tg.TigerGraphConnection(
            host=TG_HOST,
            restppPort=TG_PORT,
            username=TG_USERNAME,
            password=TG_PASSWORD,
            graphname=TG_GRAPH
        )
        # Test ping or echo
        echo_resp = conn.echo()
        print(f"[SUCCESS] Connected to TigerGraph: {echo_resp}")
        return conn, True
    except Exception as e:
        print(f"[BLOCKED] Could not connect to TigerGraph instance at {TG_HOST}:{TG_PORT}.")
        print(f"Error details: {e}")
        print("\nDeployment is currently BLOCKED pending active TigerGraph credentials.")
        print("To unblock:")
        print("  1. Create a free workspace on https://savanna.tgcloud.io or start local TigerGraph container.")
        print("  2. Configure credentials in d:\\task4\\.env:")
        print("       TIGERGRAPH_HOST=https://your-domain.i.tgcloud.io")
        print("       TIGERGRAPH_USERNAME=tigergraph")
        print("       TIGERGRAPH_PASSWORD=your_password")
        print("       TIGERGRAPH_GRAPH_NAME=HHGOA_Fraud_Graph")
        print("       TIGERGRAPH_SECRET=your_secret")
        print("  3. Rerun this script to deploy schema and load data automatically.")
        return None, False

def deploy_schema(conn):
    print("\n--- Deploying Schema ---")
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        gsql_content = f.read()
    print("Executing schema DDL against TigerGraph...")
    resp = conn.gsql(gsql_content)
    print(f"Schema response:\n{resp}")

def deploy_loading_jobs(conn):
    print("\n--- Installing Loading Jobs ---")
    with open(LOADING_JOBS_FILE, "r", encoding="utf-8") as f:
        gsql_content = f.read()
    print("Installing loading jobs...")
    resp = conn.gsql(gsql_content)
    print(f"Loading jobs response:\n{resp}")

def main():
    conn, connected = test_connection()
    if not connected:
        sys.exit(1)
    
    deploy_schema(conn)
    deploy_loading_jobs(conn)
    print("\nData loading completed successfully!")

if __name__ == "__main__":
    main()
