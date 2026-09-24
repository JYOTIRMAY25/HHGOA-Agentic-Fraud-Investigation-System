import pandas as pd

txns = pd.read_csv('D:/task4/transactions.csv', usecols=['TransactionID', 'customer_id', 'card1', 'ts', 'channel', 'TransactionAmt', 'risk_score', 'addr1', 'addr2', 'ProductCD'])

# Check how many unique card1 per customer
card_per_cust = txns.groupby('customer_id')['card1'].nunique()
print('Card1 per customer distribution:')
print(card_per_cust.value_counts())
print()
print('Customers with multiple card1:')
multi = card_per_cust[card_per_cust > 1]
print(multi)
print()

# Check the flagged transactions in case pack
cases = pd.read_csv('D:/task4/case_pack.csv')
for _, case in cases.iterrows():
    flagged_id = case['flagged_txn_id']
    txn = txns[txns['TransactionID'] == int(flagged_id)]
    if len(txn) > 0:
        print('Case {}: Flagged txn {} -> card1={}, customer_id={}, amt={}, channel={}, addr1={}, addr2={}, ProductCD={}, risk_score={}'.format(
            case['case_id'], flagged_id, txn['card1'].values[0], txn['customer_id'].values[0],
            txn['TransactionAmt'].values[0], txn['channel'].values[0], txn['addr1'].values[0],
            txn['addr2'].values[0], txn['ProductCD'].values[0], txn['risk_score'].values[0]
        ))
    else:
        print('Case {}: Flagged txn {} NOT FOUND'.format(case['case_id'], flagged_id))