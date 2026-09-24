#!/usr/bin/env python3
"""Install and verify shortestPath query."""
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
conn.useGraph(graphname)

# Try to install the query
print("Installing query...")
try:
    r = conn.installQueries("shortestPath")
    print(f"installQueries: {r}")
except Exception as e:
    print(f"installQueries error: {type(e).__name__}: {str(e)[:300]}")

# Check query status
print("\nChecking query info...")
try:
    r = conn.getQueryInfo("shortestPath")
    print(f"getQueryInfo: {r}")
except Exception as e:
    print(f"getQueryInfo error: {type(e).__name__}: {str(e)[:200]}")

# Check installation status
print("\nChecking installation status...")
try:
    r = conn.getQueryInstallationStatus("shortestPath")
    print(f"getQueryInstallationStatus: {r}")
except Exception as e:
    print(f"getQueryInstallationStatus error: {type(e).__name__}: {str(e)[:200]}")

# Check query content
print("\nChecking query content...")
try:
    r = conn.getQueryContent("shortestPath")
    print(f"getQueryContent: {str(r)[:500]}")
except Exception as e:
    print(f"getQueryContent error: {type(e).__name__}: {str(e)[:200]}")

# listQueryNames
print("\nListing query names...")
try:
    r = conn.listQueryNames()
    print(f"listQueryNames: {r}")
except Exception as e:
    print(f"listQueryNames error: {type(e).__name__}: {str(e)[:200]}")
