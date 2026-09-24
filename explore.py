import pandas as pd

cases = pd.read_csv('D:/task4/case_pack.csv')
print('Case card_ids:')
for _, row in cases.iterrows():
    print('  {}: card_id={}, customer_id={}'.format(row['case_id'], row['card_id'], row['customer_id']))

txns = pd.read_csv('D:/task4/transactions.csv', usecols=['TransactionID', 'customer_id', 'card1', 'ts', 'channel', 'TransactionAmt', 'risk_score', 'addr1', 'addr2', 'ProductCD'])
print()
print('Sample customer C12382 transactions:')
cust_txns = txns[txns['customer_id'] == 'C12382']
print(cust_txns[['TransactionID', 'card1', 'ts', 'channel', 'TransactionAmt', 'addr1', 'addr2']].head(10))
print()
print('Unique card1 values for C12382:', cust_txns['card1'].unique())

print()
print('Sample customer C08623 transactions:')
cust_txns = txns[txns['customer_id'] == 'C08623']
print(cust_txns[['TransactionID', 'card1', 'ts', 'channel', 'TransactionAmt', 'addr1', 'addr2']].head(10))
print()
print('Unique card1 values for C08623:', cust_txns['card1'].unique())