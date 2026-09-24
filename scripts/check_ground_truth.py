import pandas as pd

cp = pd.read_csv('case_pack.csv')
print('case_pack columns:', cp.columns.tolist())
print(cp[['case_id','trigger_type','flagged_txn_id','card_id','customer_id','risk_score']].to_string())

cc = pd.read_csv('closed_cases_history.csv')
print('\nclosed_cases columns:', cc.columns.tolist())
print('closed_cases outcomes:', cc['outcome'].value_counts().to_dict())

# Check if any case_pack IDs appear in closed_cases
cp_ids = set(cp['case_id'].tolist())
cc_ids = set(cc['case_id'].tolist())
overlap = cp_ids & cc_ids
print('\ncase_pack IDs in closed_cases:', overlap)

# Check transactions.csv for fraud flag
import csv
with open('transactions.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)
print('\ntransactions.csv columns (first 10):', header[:10])
print('transactions.csv columns (last 10):', header[-10:])
fraud_cols = [c for c in header if 'fraud' in c.lower() or 'label' in c.lower() or 'target' in c.lower()]
print('fraud-related columns:', fraud_cols)
