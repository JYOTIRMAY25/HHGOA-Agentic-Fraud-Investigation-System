import pandas as pd
cc = pd.read_csv('closed_cases_history.csv')
# Check customers with multiple card_ids
cust_cards = cc.groupby('customer_id')['card_id'].apply(lambda x: list(set(x))).reset_index()
multi_card = cust_cards[cust_cards['card_id'].apply(len) > 1]
print(f"Customers with multiple card_ids in closed cases: {len(multi_card)}")
print(multi_card.head(20).to_string())