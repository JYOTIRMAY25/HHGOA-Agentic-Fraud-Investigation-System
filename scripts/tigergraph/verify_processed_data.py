"""Phase 7: Verify processed data CSV files.
Lists every CSV in data/processed/ with row/column counts and intended graph entity.
"""

import os
import csv

print("=" * 60)
print("HHGOA PROCESSED DATA VERIFICATION")
print("=" * 60)

PROCESSED_DIR = "D:/task4/data/processed"

if not os.path.exists(PROCESSED_DIR):
    print("\nERROR: data/processed/ directory does not exist!")
    print("Run: python scripts/tigergraph/prepare_graph_data.py to generate processed files.")
    exit(1)

files = sorted([f for f in os.listdir(PROCESSED_DIR) if f.endswith('.csv')])
print(f"\nFound {len(files)} CSV files in data/processed/\n")

# Map files to graph entities
entity_map = {
    "vertices_customer.csv": "Customer",
    "vertices_card.csv": "Card",
    "vertices_transaction.csv": "Transaction",
    "vertices_device_profile.csv": "DeviceProfile",
    "vertices_email_domain.csv": "EmailDomain",
    "vertices_billing_region.csv": "BillingRegion",
    "vertices_fraud_case.csv": "FraudCase",
    "vertices_fraud_pattern.csv": "FraudPattern",
    "vertices_policy_rule.csv": "PolicyRule",
    "edges_owns.csv": "OWNS (Customer -> Card)",
    "edges_performs.csv": "PERFORMS (Card -> Transaction)",
    "edges_next_transaction.csv": "NEXT_TRANSACTION (Txn -> Txn)",
    "edges_used_device.csv": "USED_DEVICE (Txn -> DeviceProfile)",
    "edges_purchaser_email.csv": "PURCHASER_EMAIL (Txn -> EmailDomain)",
    "edges_recipient_email.csv": "RECIPIENT_EMAIL (Txn -> EmailDomain)",
    "edges_billed_in.csv": "BILLED_IN (Txn -> BillingRegion)",
    "edges_investigates_txn.csv": "INVESTIGATES_TXN (Case -> Txn)",
    "edges_targets_card.csv": "TARGETS_CARD (Case -> Card)",
    "edges_connects_to_card.csv": "CONNECTS_TO_CARD (Case -> Card)",
    "edges_investigates_customer.csv": "INVESTIGATES_CUSTOMER (Case -> Customer)",
    "edges_exhibits_pattern.csv": "EXHIBITS_PATTERN (Case -> FraudPattern)",
    "edges_governed_by.csv": "GOVERNED_BY (Case -> PolicyRule)",
}

total_rows = 0
for f in files:
    path = os.path.join(PROCESSED_DIR, f)
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            reader = csv.reader(fh)
            header = next(reader, None)
            row_count = sum(1 for _ in reader)
        total_rows += row_count
        entity = entity_map.get(f, "Unknown")
        col_count = len(header) if header else 0
        # Check column limit (TigerGraph CSV import limit is typically 512 columns)
        col_status = "OK" if col_count <= 512 else "EXCEEDS LIMIT"
        print(f"  {f}")
        print(f"    Entity: {entity}")
        print(f"    Rows: {row_count:,}")
        print(f"    Columns: {col_count} ({col_status})")
    except Exception as e:
        print(f"  {f}: ERROR - {e}")

print(f"\nTotal rows across all files: {total_rows:,}")

# Check raw transactions.csv column count
raw_path = "D:/task4/transactions.csv"
if os.path.exists(raw_path):
    with open(raw_path, 'r', encoding='utf-8') as fh:
        reader = csv.reader(fh)
        header = next(reader, None)
        raw_cols = len(header) if header else 0
    print(f"\nRaw transactions.csv columns: {raw_cols}")
    if raw_cols > 512:
        print("  WARNING: Raw transactions.csv has {raw_cols} columns - exceeds TigerGraph CSV import limit!".format(raw_cols=raw_cols))
        print("  MUST use processed graph-specific CSV files, NOT raw transactions.csv")
    else:
        print("  OK: Within CSV import limit")

print("\n" + "=" * 60)
print("PROCESSED DATA VERIFICATION COMPLETE")
print("=" * 60)