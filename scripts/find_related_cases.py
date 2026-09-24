import pandas as pd

df = pd.read_csv('closed_cases_history.csv')
cp = pd.read_csv('case_pack.csv')

print('CP customers:', cp['customer_id'].tolist())
print('DF customers sample:', df['customer_id'].tolist()[:5])

customers = set(cp['customer_id'].tolist())
cards = set(cp['card_id'].tolist())
mask = df['customer_id'].isin(customers) | df['card_id'].isin(cards)
related = df[mask]
print('Related:', len(related))
print(related[['case_id','customer_id','card_id','outcome','pattern','exposure_usd']].to_string())
