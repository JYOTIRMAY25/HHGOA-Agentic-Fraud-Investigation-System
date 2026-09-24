"""
HHGOA TigerGraph MCP Configuration Module
Loads and validates connection parameters from environment variables without
exposing secrets. Uses the official TigerGraph MCP environment variable names.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class MCPConfig:
    """Configuration resolved from environment variables.

    Variable names follow the official TigerGraph MCP convention (``TG_*``)
    so the same .env works for tigergraph-mcp and this custom investigation
    server. Legacy ``TIGERGRAPH_*`` aliases are kept for backward compat
    with Phase 2 scripts.
    """

    # --- TigerGraph connection (official TG_* variables) ---
    TG_HOST = os.getenv("TG_HOST") or os.getenv("TIGERGRAPH_HOST") or "http://127.0.0.1"
    TG_GRAPHNAME = os.getenv("TG_GRAPHNAME") or os.getenv("TIGERGRAPH_GRAPH_NAME") or "HHGOA_Fraud_Graph"
    TG_USERNAME = os.getenv("TG_USERNAME") or os.getenv("TIGERGRAPH_USERNAME") or "tigergraph"
    TG_PASSWORD = os.getenv("TG_PASSWORD") or os.getenv("TIGERGRAPH_PASSWORD") or "tigergraph"
    TG_SECRET = os.getenv("TG_SECRET") or os.getenv("TIGERGRAPH_SECRET") or ""
    TG_API_TOKEN = os.getenv("TG_API_TOKEN") or os.getenv("TG_TOKEN") or ""
    TG_JWT_TOKEN = os.getenv("TG_JWT_TOKEN") or ""

    # Optional topology overrides
    TG_RESTPP_PORT = os.getenv("TG_RESTPP_PORT") or os.getenv("TIGERGRAPH_PORT") or "9000"
    TG_GS_PORT = os.getenv("TG_GS_PORT") or "14240"
    TG_SSL_PORT = os.getenv("TG_SSL_PORT") or "443"
    TG_TGCLOUD = os.getenv("TG_TGCLOUD", "false").strip().lower() in ("true", "1", "yes")
    TG_CERT_PATH = os.getenv("TG_CERT_PATH") or ""

    # --- MCP server network settings ---
    SERVER_HOST = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
    SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8000"))
    TRANSPORT = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()
    MOUNT_PATH = os.getenv("MCP_MOUNT_PATH", "/mcp/")

    # --- Investigation tool configuration ---
    TG_DEFAULT_PROFILE = os.getenv("TG_DEFAULT_PROFILE") or os.getenv("TG_PROFILE") or "default"

    # --- Testing & offline mode ---
    TG_MOCK_MODE = os.getenv("TG_MOCK_MODE", "false").strip().lower() in ("true", "1", "yes")

    # --- Tool filtering (security policy) ---
    TG_ALLOWED_TOOLS = os.getenv("TG_ALLOWED_TOOLS", "")
    TG_BLOCKED_TOOLS = os.getenv("TG_BLOCKED_TOOLS", "")

    # Investigation tools only - everything else blocked by default
    DEFAULT_ALLOWED_TOOLS = [
        "investigate_transaction",
        "trace_connected_entities",
        "detect_card_testing",
        "analyze_region_anomalies",
        "retrieve_similar_cases",
        "calculate_case_exposure",
        "validate_graph_metrics",
    ]

    # Hard-blocked operations (never exposed even if requested)
    BLOCKED_TOOLS = frozenset({
        "gsql",
        "generate_gsql",
        "generate_cypher",
        "drop_graph",
        "clear_graph_data",
        "delete_node",
        "delete_nodes",
        "delete_edge",
        "delete_edges",
        "update_schema",
        "add_node",
        "add_nodes",
        "add_edge",
        "add_edges",
        "run_query",
        "upsert_vectors",
        "load_vectors_from_csv",
        "load_vectors_from_json",
        "update_data_source",
        "drop_data_source",
        "drop_all_data_sources",
        "drop_loading_job",
        "drop_query",
    })

    # Query timeout in seconds
    QUERY_TIMEOUT = float(os.getenv("TG_QUERY_TIMEOUT", "30"))

    @classmethod
    def get_sanitized_summary(cls) -> dict:
        """Returns safe connection summary with masked credentials."""
        auth_mode = "token" if cls.TG_API_TOKEN or cls.TG_JWT_TOKEN else (
            "password" if cls.TG_USERNAME else "none"
        )
        return {
            "host": cls.TG_HOST,
            "port": cls.TG_RESTPP_PORT,
            "graph": cls.TG_GRAPHNAME,
            "username": cls.TG_USERNAME,
            "auth_mode": auth_mode,
            "has_password": bool(cls.TG_PASSWORD),
            "has_secret": bool(cls.TG_SECRET),
            "has_token": bool(cls.TG_API_TOKEN or cls.TG_JWT_TOKEN),
            "is_tgcloud": cls.TG_TGCLOUD,
            "mock_mode": cls.TG_MOCK_MODE,
            "transport": cls.TRANSPORT,
        }
