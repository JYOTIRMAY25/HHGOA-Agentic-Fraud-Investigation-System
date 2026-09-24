import pandas as pd

# Check closed cases
closed = pd.read_csv('D:/task4/closed_cases_history.csv')
print('Closed cases:', len(closed))
print('Outcomes:', closed['outcome'].value_counts())
print('Patterns:', closed['pattern'].value_counts())
print()

# Check for patterns in closed cases
for pattern in ['card_testing', 'card_not_present_fraud', 'card_not_present_new_device', 'out_of_region_use', 'account_takeover', 'undocumented', 'none']:
    subset = closed[closed['pattern'] == pattern]
    if len(subset) > 0:
        print('Pattern {}: {} cases'.format(pattern, len(subset)))
        if pattern != 'none':
            print('  Example:', subset.iloc[0]['case_id'], subset.iloc[0]['analyst_notes'][:100] if pd.notna(subset.iloc[0]['analyst_notes']) else '')

# Check if any closed cases involve the same customers as our 20 cases
cases = pd.read_csv('D:/task4/case_pack.csv')
case_customers = set(cases['customer_id'].unique())
print()
print('Case pack customers:', case_customers)
overlap = closed[closed['customer_id'].isin(case_customers)]
print('Closed cases for case pack customers:', len(overlap))
for _, row in overlap.iterrows():
    print('  {}: customer={}, card={}, outcome={}, pattern={}, exposure={}'.format(
        row['case_id'], row['customer_id'], row['card_id'], row['outcome'], row['pattern'], row['exposure_usd']
    ))

# Also check for shared card1 values (not customer_id)
txns = pd.read_csv('D:/task4/transactions.csv', usecols=['TransactionID', 'customer_id', 'card1'])
case_cards = {}
for _, case in cases.iterrows():
    flagged_id = case['flagged_txn_id']
    txn = txns[txns['TransactionID'] == int(flagged_id)]
    if len(txn) > 0:
        case_cards[case['case_id']] = txn['card1'].values[0]

print()
print('Case card1 values:')
for cid, c1 in case_cards.items():
    print('  {}: card1={}'.format(cid, c1))

# Check closed cases for same card1
closed_cards = set()
for _, row in closed.iterrows():
    if pd.notna(row['card_id']):
        # card_id is like C00259-K1, need to map to card1
        pass