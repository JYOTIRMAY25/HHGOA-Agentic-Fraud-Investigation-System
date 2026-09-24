import pandas as pd

# Check identity data for online transactions
identity = pd.read_csv('D:/task4/identity.csv')
print('Identity records:', len(identity))
print('Columns:', identity.columns.tolist())

# Check for flagged transactions in identity
cases = pd.read_csv('D:/task4/case_pack.csv')
for _, case in cases.iterrows():
    flagged_id = case['flagged_txn_id']
    id_rec = identity[identity['TransactionID'] == int(flagged_id)]
    if len(id_rec) > 0:
        row = id_rec.iloc[0]
        print('Case {}: Flagged txn {} -> DeviceType={}, DeviceInfo={}, id_15={}, id_30={}, id_31={}, id_33={}, id_34={}'.format(
            case['case_id'], flagged_id, row['DeviceType'], row['DeviceInfo'],
            row['id_15'], row['id_30'], row['id_31'], row['id_33'], row['id_34']
        ))
    else:
        print('Case {}: Flagged txn {} - NO IDENTITY RECORD (in_person)'.format(case['case_id'], flagged_id))