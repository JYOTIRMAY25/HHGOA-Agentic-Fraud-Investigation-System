import pandas as pd

cp = pd.read_csv('case_pack.csv')
txn_ids = cp['flagged_txn_id'].astype(str).tolist()

chunks = pd.read_csv('transactions.csv', chunksize=50000,
                     usecols=['TransactionID','TransactionAmt','ProductCD','card1','card6',
                              'addr1','addr2','P_emaildomain','R_emaildomain',
                              'customer_id','ts','channel','risk_score'])
hits = []
needed = set(txn_ids)
for chunk in chunks:
    chunk['TransactionID'] = chunk['TransactionID'].astype(str)
    found = chunk[chunk['TransactionID'].isin(needed)]
    if len(found):
        hits.append(found)
        needed -= set(found['TransactionID'].tolist())
    if not needed:
        break

result = pd.concat(hits) if hits else pd.DataFrame()
print(result.to_string())
result.to_csv('scripts/flagged_txns.csv', index=False)
print('\nMissing:', needed)
