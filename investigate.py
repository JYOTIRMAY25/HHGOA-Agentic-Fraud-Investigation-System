"""
HHGOA Fraud Investigation System
Investigates 20 cases from case_pack.csv and produces JSON answer files.
"""
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

# ============================================================
# DATA LOADING
# ============================================================
print("Loading data...")
txns = pd.read_csv('transactions.csv')
identity = pd.read_csv('identity.csv')
closed_cases = pd.read_csv('closed_cases_history.csv')
case_pack = pd.read_csv('case_pack.csv')

print(f"Transactions: {len(txns)}, Identity: {len(identity)}, Closed cases: {len(closed_cases)}")

# Merge identity with transactions for online transactions
txns['is_online'] = txns['ProductCD'] != 'W'
txns_with_id = txns.merge(identity, on='TransactionID', how='left')
print(f"Transactions with identity: {txns_with_id['id_15'].notna().sum()}")

# Build card_id from customer_id and card1
# card_id format: CXXXXX-KX where XXXXX is customer number and KX is card index
# card1 in transactions is an issuer code
# We need to map: for each customer, card1 values to card indices
# The card_id in case_pack is like C12382-K1
# Let's figure out the card index mapping
# For a customer, cards are numbered K1, K2, etc.
# We need to map card1 (issuer code) to card index

# Let's check: for customer C12382, what card1 values exist?
c12382 = txns[txns['customer_id']=='C12382']
print(f"\nCustomer C12382 transactions:")
print(c12382[['TransactionID','card1','ProductCD','channel','TransactionAmt','ts']].to_string())