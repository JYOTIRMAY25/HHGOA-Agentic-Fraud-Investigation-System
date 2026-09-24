import pandas as pd, json

cp = pd.read_csv('case_pack.csv')
flagged = pd.read_csv('scripts/flagged_txns.csv')
cards = cp['card_id'].tolist()
customers = cp['customer_id'].tolist()

# Map card_id -> card1 (issuer code used to group transactions)
card1_map = dict(zip(flagged['customer_id'], flagged['card1']))

# Get all transactions for these customers (last 90 days window)
chunks = pd.read_csv('transactions.csv', chunksize=50000,
    usecols=['TransactionID','TransactionAmt','ProductCD','card1','addr1','addr2',
             'P_emaildomain','customer_id','ts','channel','risk_score','D1'])
history = []
card1_set = set(flagged['card1'].tolist())
for chunk in chunks:
    found = chunk[chunk['card1'].isin(card1_set)]
    if len(found):
        history.append(found)

hist_df = pd.concat(history) if history else pd.DataFrame()
hist_df['ts'] = pd.to_datetime(hist_df['ts'])
hist_df = hist_df.sort_values('ts')

# Per-card summary: count, regions, date range, amounts
summary = {}
for cust in customers:
    c1 = card1_map.get(cust)
    if not c1:
        continue
    sub = hist_df[hist_df['card1'] == c1]
    if sub.empty:
        summary[cust] = {}
        continue
    regions = sub['addr1'].dropna().value_counts().head(5).to_dict()
    summary[cust] = {
        'txn_count': len(sub),
        'date_range': [str(sub['ts'].min()), str(sub['ts'].max())],
        'avg_amount': round(sub['TransactionAmt'].mean(), 2),
        'channels': sub['channel'].value_counts().to_dict(),
        'top_regions': {str(k): int(v) for k, v in regions.items()},
        'product_codes': sub['ProductCD'].value_counts().to_dict(),
    }

print(json.dumps(summary, indent=2))

# Identity records for the 20 flagged txns
txn_ids = set(cp['flagged_txn_id'].astype(str).tolist())
id_chunks = pd.read_csv('identity.csv', chunksize=20000,
    usecols=['TransactionID','DeviceType','DeviceInfo','id_15','id_23','id_30','id_31','id_33'])
id_hits = []
for chunk in id_chunks:
    chunk['TransactionID'] = chunk['TransactionID'].astype(str)
    found = chunk[chunk['TransactionID'].isin(txn_ids)]
    if len(found):
        id_hits.append(found)

id_df = pd.concat(id_hits) if id_hits else pd.DataFrame()
print('\nIDENTITY RECORDS:')
print(id_df.to_string())
