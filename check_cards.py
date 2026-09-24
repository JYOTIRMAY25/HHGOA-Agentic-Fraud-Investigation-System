import pandas as pd
txns = pd.read_csv('transactions.csv')

# Check customers with multiple card1 values
for cust in ['C08623', 'C09933', 'C11923', 'C05876', 'C07671', 'C02354', 'C07987', 'C12265']:
    cust_txns = txns[txns['customer_id'] == cust]
    card1s = cust_txns['card1'].unique()
    print(f"{cust}: card1 values = {card1s}, n_txns = {len(cust_txns)}")
    # Check card2, card3, etc.
    for col in ['card2', 'card3', 'card5']:
        vals = cust_txns[col].dropna().unique()
        if len(vals) > 0:
            print(f"  {col}: {vals[:5]}")
    print()