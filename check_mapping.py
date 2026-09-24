import pandas as pd
txns = pd.read_csv('transactions.csv')
# Check: for customer C12382, what card1 values exist?
c12382 = txns[txns['customer_id']=='C12382']
print('Customer C12382 unique card1 values:', c12382['card1'].unique())
print()

# Check the case pack
cases = pd.read_csv('case_pack.csv')
for _, row in cases.iterrows():
    cid = row['customer_id']
    card_id = row['card_id']
    txn_id = str(row['flagged_txn_id'])
    txn_row = txns[txns['TransactionID'].astype(str) == txn_id]
    if len(txn_row) > 0:
        card1 = txn_row.iloc[0]['card1']
        print(f"{row['case_id']}: customer={cid}, card_id={card_id}, card1={card1}, txn={txn_id}")