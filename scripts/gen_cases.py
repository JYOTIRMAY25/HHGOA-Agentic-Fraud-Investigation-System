import json, os, pandas as pd

os.makedirs('cases', exist_ok=True)

# Flagged transaction data (from lookup_txns.py output)
TXN = {
    "3514030": {"amt":77.07,"ch":"in_person","prod":"W","addr1":444.0,"addr2":87.0,"risk":0.61,"email_p":None,"email_r":None},
    "3478782": {"amt":292.36,"ch":"online","prod":"C","addr1":None,"addr2":None,"risk":0.79,"email_p":"hotmail.com","email_r":"hotmail.com"},
    "3530164": {"amt":49.00,"ch":"in_person","prod":"W","addr1":330.0,"addr2":87.0,"risk":0.40,"email_p":None,"email_r":None},
    "3583227": {"amt":128.33,"ch":"online","prod":"C","addr1":None,"addr2":None,"risk":0.34,"email_p":"hotmail.com","email_r":"hotmail.com"},
    "3523199": {"amt":100.07,"ch":"online","prod":"R","addr1":330.0,"addr2":87.0,"risk":0.54,"email_p":"icloud.com","email_r":"gmail.com"},
    "3476682": {"amt":482.12,"ch":"online","prod":"C","addr1":264.0,"addr2":87.0,"risk":0.25,"email_p":"gmail.com","email_r":None},
    "3514948": {"amt":111.92,"ch":"in_person","prod":"W","addr1":264.0,"addr2":87.0,"risk":0.87,"email_p":None,"email_r":None},
    "3558054": {"amt":55.68,"ch":"online","prod":"C","addr1":None,"addr2":None,"risk":0.38,"email_p":"hotmail.com","email_r":"hotmail.com"},
    "3581141": {"amt":30.02,"ch":"online","prod":"S","addr1":203.0,"addr2":87.0,"risk":0.28,"email_p":None,"email_r":"gmail.com"},
    "3506725": {"amt":1000.03,"ch":"online","prod":"R","addr1":469.0,"addr2":87.0,"risk":0.90,"email_p":"anonymous.com","email_r":"anonymous.com"},
    "3583368": {"amt":131.30,"ch":"online","prod":"C","addr1":None,"addr2":None,"risk":0.39,"email_p":"gmail.com","email_r":"gmail.com"},
    "3553342": {"amt":30.91,"ch":"in_person","prod":"W","addr1":494.0,"addr2":87.0,"risk":0.55,"email_p":None,"email_r":None},
    "3526826": {"amt":35.66,"ch":"online","prod":"C","addr1":None,"addr2":None,"risk":0.76,"email_p":"gmail.com","email_r":"gmail.com"},
    "3478561": {"amt":74.96,"ch":"online","prod":"C","addr1":191.0,"addr2":87.0,"risk":0.05,"email_p":"yahoo.com","email_r":"gmail.com"},
    "3464869": {"amt":599.94,"ch":"online","prod":"R","addr1":327.0,"addr2":87.0,"risk":0.77,"email_p":"anonymous.com","email_r":"anonymous.com"},
    "3534820": {"amt":59.67,"ch":"online","prod":"C","addr1":None,"addr2":None,"risk":0.37,"email_p":"hotmail.com","email_r":"hotmail.com"},
    "3450629": {"amt":100.09,"ch":"online","prod":"R","addr1":204.0,"addr2":87.0,"risk":0.57,"email_p":"anonymous.com","email_r":"anonymous.com"},
    "3491361": {"amt":39.08,"ch":"in_person","prod":"W","addr1":126.0,"addr2":87.0,"risk":0.48,"email_p":None,"email_r":None},
    "3503878": {"amt":99.92,"ch":"online","prod":"R","addr1":264.0,"addr2":87.0,"risk":0.90,"email_p":"verizon.net","email_r":"gmail.com"},
    "3509359": {"amt":125.08,"ch":"online","prod":"R","addr1":264.0,"addr2":87.0,"risk":0.52,"email_p":"yahoo.com","email_r":"cox.net"},
}

# Identity records for online transactions
ID = {
    "3450629": {"id_15":"Found","id_23":"IP_PROXY:HIDDEN","id_30":"Windows 10","id_31":"chrome 65.0","id_33":"1920x1080","DeviceType":"desktop","DeviceInfo":"Windows"},
    "3464869": {"id_15":"New","id_23":None,"id_30":"Windows 8.1","id_31":"ie 11.0 for desktop","id_33":"1680x1050","DeviceType":"desktop","DeviceInfo":"Trident/7.0"},
    "3476682": {"id_15":"New","id_23":None,"id_30":"Windows 7","id_31":"ie 11.0 for desktop","id_33":"1920x1080","DeviceType":"desktop","DeviceInfo":"Trident/7.0"},
    "3478561": {"id_15":"New","id_23":"IP_PROXY:ANONYMOUS","id_30":"Android 7.0","id_31":"chrome 62.0 for android","id_33":"1920x1080","DeviceType":"mobile","DeviceInfo":"SM-G935F Build/NRD90M"},
    "3478782": {"id_15":None,"id_23":None,"id_30":None,"id_31":None,"id_33":None,"DeviceType":None,"DeviceInfo":None},
    "3503878": {"id_15":"New","id_23":None,"id_30":"other","id_31":"chrome 61.0","id_33":"1280x720","DeviceType":"desktop","DeviceInfo":"Windows"},
    "3506725": {"id_15":"New","id_23":None,"id_30":"Windows 10","id_31":"edge 16.0","id_33":"1366x768","DeviceType":"desktop","DeviceInfo":"Windows"},
    "3509359": {"id_15":"New","id_23":None,"id_30":"Windows 10","id_31":"ie 11.0 for desktop","id_33":"1920x1080","DeviceType":"desktop","DeviceInfo":"Trident/7.0"},
    "3523199": {"id_15":"New","id_23":None,"id_30":"iOS 9.3.5","id_31":"mobile safari 9.0","id_33":"1024x768","DeviceType":"mobile","DeviceInfo":"iOS Device"},
    "3526826": {"id_15":"New","id_23":None,"id_30":None,"id_31":"chrome 66.0","id_33":None,"DeviceType":"desktop","DeviceInfo":None},
    "3534820": {"id_15":"New","id_23":None,"id_30":None,"id_31":"edge 16.0","id_33":None,"DeviceType":"desktop","DeviceInfo":"Windows"},
    "3558054": {"id_15":"Found","id_23":None,"id_30":None,"id_31":"chrome 66.0","id_33":None,"DeviceType":"desktop","DeviceInfo":None},
    "3581141": {"id_15":"Found","id_23":None,"id_30":None,"id_31":None,"id_33":None,"DeviceType":"desktop","DeviceInfo":None},
    "3583227": {"id_15":"New","id_23":None,"id_30":None,"id_31":"firefox 47.0","id_33":None,"DeviceType":"desktop","DeviceInfo":None},
    "3583368": {"id_15":"New","id_23":None,"id_30":None,"id_31":"chrome 66.0 for android","id_33":None,"DeviceType":"mobile","DeviceInfo":"SM-G610F Build/NRD90M"},
}

# Card history summary (from card_history.py output)
HIST = {
    "C12382": {"txn_count":422,"channels":{"in_person":420,"online":2},"top_regions":{"204.0":47,"264.0":35,"512.0":34,"272.0":30,"433.0":23},"product_codes":{"W":420,"H":2},"avg_amount":115.6},
    "C11891": {"txn_count":44,"channels":{"online":44},"top_regions":{"375.0":1},"product_codes":{"C":44},"avg_amount":47.46},
    "C08623": {"txn_count":1140,"channels":{"in_person":1086,"online":54},"top_regions":{"299.0":123,"204.0":99,"315.0":88,"264.0":81,"325.0":54},"product_codes":{"W":1086,"H":26,"S":16,"R":12},"avg_amount":129.36},
    "C08106": {"txn_count":216,"channels":{"online":216},"top_regions":{"284.0":3,"465.0":2,"161.0":1,"431.0":1},"product_codes":{"C":216},"avg_amount":35.52},
    "C02923": {"txn_count":92,"channels":{"in_person":70,"online":22},"top_regions":{"330.0":87,"272.0":2,"299.0":1,"126.0":1,"324.0":1},"product_codes":{"W":70,"S":8,"H":7,"R":7},"avg_amount":176.02},
    "C07297": {"txn_count":261,"channels":{"in_person":255,"online":6},"top_regions":{"264.0":34,"485.0":30,"191.0":25,"315.0":17,"204.0":14},"product_codes":{"W":255,"C":4,"H":2},"avg_amount":112.56},
    "C09933": {"txn_count":2792,"channels":{"in_person":2549,"online":243},"top_regions":{"264.0":2552,"204.0":36,"325.0":22,"299.0":20,"387.0":19},"product_codes":{"W":2549,"H":155,"R":69,"C":16,"S":3},"avg_amount":123.85},
    "C13171": {"txn_count":928,"channels":{"online":927,"in_person":1},"top_regions":{"284.0":23,"465.0":9,"161.0":6,"130.0":5,"511.0":2},"product_codes":{"C":927,"W":1},"avg_amount":54.27},
    "C08299": {"txn_count":56,"channels":{"online":50,"in_person":6},"top_regions":{"330.0":33,"204.0":11,"441.0":4,"337.0":3,"184.0":2},"product_codes":{"S":49,"W":6,"H":1},"avg_amount":61.17},
    "C10434": {"txn_count":36,"channels":{"in_person":18,"online":18},"top_regions":{"469.0":27,"220.0":4,"272.0":2,"330.0":1,"418.0":1},"product_codes":{"W":18,"R":11,"H":7},"avg_amount":153.87},
    "C11923": {"txn_count":10361,"channels":{"online":10361},"top_regions":{"284.0":95,"465.0":71,"130.0":54,"161.0":51,"511.0":34},"product_codes":{"C":10360,"R":1},"avg_amount":39.45},
    "C05876": {"txn_count":991,"channels":{"in_person":930,"online":61},"top_regions":{"325.0":126,"272.0":99,"204.0":81,"264.0":81,"330.0":76},"product_codes":{"W":930,"S":30,"H":18,"R":13},"avg_amount":80.06},
    "C07671": {"txn_count":1569,"channels":{"in_person":1547,"online":22},"top_regions":{"264.0":1343,"310.0":106,"110.0":78,"387.0":14,"272.0":5},"product_codes":{"W":1547,"H":16,"R":4,"C":2},"avg_amount":112.42},
    "C13487": {"txn_count":85,"channels":{"in_person":81,"online":4},"top_regions":{"191.0":44,"272.0":41},"product_codes":{"W":81,"C":3,"R":1},"avg_amount":57.43},
    "C03042": {"txn_count":79,"channels":{"online":61,"in_person":18},"top_regions":{"325.0":12,"299.0":10,"337.0":8,"330.0":7,"387.0":4},"product_codes":{"R":28,"H":19,"W":18,"S":9,"C":5},"avg_amount":144.57},
    "C09988": {"txn_count":61,"channels":{"online":61},"top_regions":{"100.0":1,"382.0":1},"product_codes":{"C":61},"avg_amount":41.81},
    "C04570": {"txn_count":59,"channels":{"online":42,"in_person":17},"top_regions":{"299.0":10,"325.0":10,"315.0":8,"264.0":7,"204.0":6},"product_codes":{"R":36,"W":17,"H":5,"S":1},"avg_amount":342.87},
    "C02354": {"txn_count":7091,"channels":{"in_person":6539,"online":552},"top_regions":{"325.0":5774,"126.0":686,"204.0":131,"231.0":121,"272.0":60},"product_codes":{"W":6539,"H":381,"R":140,"C":26,"S":5},"avg_amount":141.15},
    "C07987": {"txn_count":248,"channels":{"in_person":185,"online":63},"top_regions":{"325.0":59,"126.0":20,"330.0":19,"299.0":19,"448.0":16},"product_codes":{"W":185,"H":39,"R":16,"S":8},"avg_amount":199.23},
    "C12265": {"txn_count":112,"channels":{"in_person":107,"online":5},"top_regions":{"264.0":112},"product_codes":{"W":107,"H":4,"R":1},"avg_amount":193.01},
}

# Prior closed cases per customer (from find_related_cases.py output)
PRIOR = {
    "C12382": ["CC-1066","CC-1673","CC-2964","CC-3587"],
    "C11891": ["CC-4160"],
    "C08623": ["CC-1589","CC-2817","CC-2935","CC-3327","CC-3682","CC-4957"],
    "C08106": ["CC-0696","CC-1736","CC-2121","CC-3778"],
    "C02923": ["CC-2400","CC-2717","CC-2857"],
    "C07297": [],
    "C09933": ["CC-0104","CC-0657","CC-0765","CC-1228","CC-1524","CC-1682","CC-2565","CC-2834","CC-2986","CC-3136","CC-3439","CC-3821","CC-4196","CC-4277","CC-4455","CC-4597","CC-4787","CC-5092","CC-5521"],
    "C13171": ["CC-0031","CC-0056","CC-0467","CC-0772","CC-1056","CC-1293","CC-1715","CC-1925","CC-2059","CC-2244","CC-2454","CC-2716","CC-3079","CC-3422","CC-3566","CC-3728","CC-3928","CC-4163","CC-4485","CC-5010"],
    "C08299": [],
    "C10434": ["CC-0873"],
    "C11923": ["CC-0031","CC-0290","CC-1056","CC-2247","CC-2673","CC-2799","CC-3039","CC-3206","CC-3905","CC-4501","CC-4743"],
    "C05876": ["CC-0003","CC-2370"],
    "C07671": ["CC-1475","CC-3216","CC-3761","CC-4294"],
    "C13487": [],
    "C03042": ["CC-0615","CC-1313","CC-3886"],
    "C09988": [],
    "C04570": ["CC-1383"],
    "C02354": ["CC-0255","CC-0405","CC-0454","CC-0631","CC-1450","CC-1699","CC-2051","CC-2187","CC-2432","CC-2589","CC-3085","CC-3537","CC-3634","CC-3899","CC-4070","CC-4436","CC-4721","CC-4942","CC-5441","CC-5558"],
    "C07987": ["CC-2011","CC-2087","CC-2860","CC-5026"],
    "C12265": ["CC-2277","CC-2447"],
}

print("Data loaded OK")
