import pandas as pd
txns = pd.read_csv('transactions.csv')

# Check customers with multiple card1 values
cust_card1 = txns.groupby('customer_id')['card1'].nunique()
multi = cust_card1[cust_card1 > 1]
print(f"Customers with multiple card1 values: {len(multi)}")
print(multi.head(20))

# Check for the case pack customers
cases = pd.read_csv('case_pack.csv')
for _, row in cases.iterrows():
    cid = row['customer_id']
    cust_txns = txns[txns['customer_id'] == cid]
    card1s = cust_txns['card1'].unique()
    print(f"{row['case_id']}: {cid} has card1 values: {card1s}")