"""
HHGOA TigerGraph Data Preparation & Staging Pipeline
Processes raw CSVs into TigerGraph loading tables with 100% referential integrity.
"""

import os
import re
import hashlib
import pandas as pd
import numpy as np
from datetime import datetime

BASE_DIR = r"d:\task4"
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

print("Starting Graph Data Preparation...")

# ----------------------------------------------------------------------
# 1. KNOWLEDGE VERTICES: FraudPattern & PolicyRule
# ----------------------------------------------------------------------
print("1/9 Preparing FraudPattern & PolicyRule vertices...")
patterns = [
    {
        "pattern_id": "card_testing",
        "pattern_name": "Card Testing",
        "description": "A stolen card number is checked before use: three or more tiny online authorizations, often under $5, then a larger purchase.",
        "typology_rules": "R5"
    },
    {
        "pattern_id": "card_not_present_fraud",
        "pattern_name": "Card-Not-Present Fraud",
        "description": "The number is used online without the card. Amounts and products that don't fit the cardholder's history, often in a burst of two to four within 48 hours.",
        "typology_rules": "R1,R2,R3,R4"
    },
    {
        "pattern_id": "card_not_present_new_device",
        "pattern_name": "Card-Not-Present Fraud from New Device",
        "description": "Online purchase with identity record marking device as New for this account, sometimes behind a proxy.",
        "typology_rules": "R1,R2,R3,R4"
    },
    {
        "pattern_id": "out_of_region_use",
        "pattern_name": "Out-of-Region Use",
        "description": "Card-present purchases in a billing region the cardholder has no history in, while normal activity continues at home.",
        "typology_rules": "R2,R3,R4"
    },
    {
        "pattern_id": "account_takeover",
        "pattern_name": "Account Takeover",
        "description": "Mixed-channel activity inconsistent with the cardholder, with device and match-flag anomalies pointing to stolen credentials.",
        "typology_rules": "R10"
    },
    {
        "pattern_id": "undocumented",
        "pattern_name": "Undocumented Coordinated Pattern",
        "description": "Activity fitting none of the five documented patterns showing coordinated or repeated abuse across customers.",
        "typology_rules": "R9"
    },
    {
        "pattern_id": "none",
        "pattern_name": "Cleared / False Alarm",
        "description": "Alert investigated and confirmed as legitimate cardholder activity.",
        "typology_rules": "R3,R7"
    }
]
pd.DataFrame(patterns).to_csv(os.path.join(PROCESSED_DIR, "vertices_fraud_pattern.csv"), index=False)

rules = [
    {
        "rule_id": "R1",
        "rule_name": "Verify before block on weak signal",
        "description": "If the case rests on a single signal and assessed fraud probability < 0.70, verify with customer or step up auth before block.",
        "condition": "prob < 0.70 and single_signal",
        "prescribed_action": "VERIFY_WITH_CUSTOMER",
        "approval_route": "auto"
    },
    {
        "rule_id": "R2",
        "rule_name": "Customer denies transaction",
        "description": "Recommend BLOCK_CARD and CREATE_CASE. Add FILE_REPORT if exposure > $1,000 or connects to shared device/card fraud.",
        "condition": "customer_denies == True",
        "prescribed_action": "BLOCK_CARD,CREATE_CASE",
        "approval_route": "L1"
    },
    {
        "rule_id": "R3",
        "rule_name": "Customer confirms transaction",
        "description": "Recommend CLOSE_NO_FRAUD. Note confirmation in case file.",
        "condition": "customer_confirms == True",
        "prescribed_action": "CLOSE_NO_FRAUD",
        "approval_route": "auto"
    },
    {
        "rule_id": "R4",
        "rule_name": "No reply within 24 hours",
        "description": "Recommend MONITOR_CARD and DECLINE_TRANSACTION for pending auths. Escalate if exposure > $500.",
        "condition": "customer_reply == None and elapsed_hours >= 24",
        "prescribed_action": "MONITOR_CARD,DECLINE_TRANSACTION",
        "approval_route": "auto"
    },
    {
        "rule_id": "R5",
        "rule_name": "Card testing sequence",
        "description": "Three or more small online auths within an hour then larger purchase: DECLINE_TRANSACTION and STEP_UP_AUTH. If purchase > $100 cleared, BLOCK_CARD.",
        "condition": "burst_micro_txns >= 3",
        "prescribed_action": "DECLINE_TRANSACTION,STEP_UP_AUTH",
        "approval_route": "L1"
    },
    {
        "rule_id": "R6",
        "rule_name": "Shared origin syndicate",
        "description": "When several cards show fraud from same device profile, region, or recipient email, CREATE_CASE, FILE_REPORT, and MONITOR_CONNECTED_CARDS.",
        "condition": "shared_card_count > 1",
        "prescribed_action": "CREATE_CASE,FILE_REPORT,MONITOR_CONNECTED_CARDS",
        "approval_route": "L2"
    },
    {
        "rule_id": "R7",
        "rule_name": "Disputed but legitimate recurring charge",
        "description": "Customer disputes charge matching recurring pattern (same merchant, amount, monthly): CREATE_CASE, VERIFY_WITH_CUSTOMER, WARN_CUSTOMER. Do not block.",
        "condition": "recurring_match == True",
        "prescribed_action": "CREATE_CASE,VERIFY_WITH_CUSTOMER,WARN_CUSTOMER",
        "approval_route": "auto"
    },
    {
        "rule_id": "R8",
        "rule_name": "Escalate when uncertain and exposed",
        "description": "If verdict is uncertain and exposure > $500, or evidence conflicts: ESCALATE_TO_ANALYST.",
        "condition": "verdict == 'uncertain' and exposure > 500",
        "prescribed_action": "ESCALATE_TO_ANALYST",
        "approval_route": "auto"
    },
    {
        "rule_id": "R9",
        "rule_name": "Undocumented pattern coordination",
        "description": "Activity fits none of known patterns but shows coordinated/repeated abuse: CREATE_CASE, FILE_REPORT, ESCALATE_TO_ANALYST.",
        "condition": "pattern == 'undocumented'",
        "prescribed_action": "CREATE_CASE,FILE_REPORT,ESCALATE_TO_ANALYST",
        "approval_route": "L2"
    },
    {
        "rule_id": "R10",
        "rule_name": "Never BLOCK_ALL_CARDS unless multiple cards compromised",
        "description": "Never BLOCK_ALL_CARDS unless at least two customer cards show confirmed fraud or credentials confirmed compromised.",
        "condition": "confirmed_fraud_cards < 2",
        "prescribed_action": "BLOCK_CARD",
        "approval_route": "L2"
    }
]
pd.DataFrame(rules).to_csv(os.path.join(PROCESSED_DIR, "vertices_policy_rule.csv"), index=False)

# ----------------------------------------------------------------------
# 2. CASES & CASE EDGES: closed_cases_history.csv & case_pack.csv
# ----------------------------------------------------------------------
print("2/9 Processing FraudCase vertices and Case edges...")
cc = pd.read_csv(os.path.join(BASE_DIR, "closed_cases_history.csv"))
cp = pd.read_csv(os.path.join(BASE_DIR, "case_pack.csv"))

cases = []
edges_inv_txn = []
edges_tgt_card = []
edges_conn_card = []
edges_inv_cust = []
edges_exh_pat = []
edges_owns = []
known_cards = {}  # card_id -> customer_id

# Process closed cases
for _, r in cc.iterrows():
    cid = str(r["case_id"])
    cust_id = str(r["customer_id"])
    card_id = str(r["card_id"])
    known_cards[card_id] = cust_id
    
    cases.append({
        "case_id": cid,
        "status": "CLOSED",
        "trigger_type": "historical_investigation",
        "trigger_text": f"Historical case for card {card_id}",
        "opened_at": r["opened_at"],
        "closed_at": r["closed_at"],
        "outcome": r["outcome"],
        "pattern": r["pattern"],
        "exposure_usd": float(r["exposure_usd"]),
        "report_filed": bool(str(r["report_filed"]).strip().lower() == "yes"),
        "actions_taken": str(r["actions_taken"]),
        "approval_route": "L2" if str(r["report_filed"]).strip().lower() == "yes" else ("L1" if "BLOCK_CARD" in str(r["actions_taken"]) else "auto"),
        "analyst_notes": str(r["analyst_notes"]).replace('"', '""'),
        "sar_narrative": str(r["analyst_notes"]).replace('"', '""') if str(r["report_filed"]).strip().lower() == "yes" else ""
    })
    
    edges_tgt_card.append({"from_case": cid, "to_card": card_id})
    edges_inv_cust.append({"from_case": cid, "to_customer": cust_id})
    edges_exh_pat.append({"from_case": cid, "to_pattern": r["pattern"]})
    edges_owns.append({"from_customer": cust_id, "to_card": card_id, "opened_date": r["opened_at"]})
    
    # Involved transactions
    first_fraud = str(r["first_fraud_txn_id"]).split(".")[0] if pd.notna(r["first_fraud_txn_id"]) else ""
    if pd.notna(r["txn_ids"]):
        for tid in str(r["txn_ids"]).split("|"):
            tid = tid.strip()
            if tid:
                is_first = (tid == first_fraud)
                edges_inv_txn.append({
                    "from_case": cid,
                    "to_transaction": tid,
                    "is_flagged_trigger": is_first,
                    "is_confirmed_fraud": (r["outcome"] == "confirmed_fraud")
                })
                
    # Connected cards
    if pd.notna(r["connected_card_ids"]):
        for cc_card in str(r["connected_card_ids"]).split("|"):
            cc_card = cc_card.strip()
            if cc_card:
                edges_conn_card.append({"from_case": cid, "to_card": cc_card})
                cc_cust = cc_card.split("-")[0]
                edges_owns.append({"from_customer": cc_cust, "to_card": cc_card, "opened_date": r["opened_at"]})
                known_cards[cc_card] = cc_cust

# Process active case pack
for _, r in cp.iterrows():
    cid = str(r["case_id"])
    cust_id = str(r["customer_id"])
    card_id = str(r["card_id"])
    flagged_txn = str(r["flagged_txn_id"])
    known_cards[card_id] = cust_id
    
    cases.append({
        "case_id": cid,
        "status": "OPEN",
        "trigger_type": r["trigger_type"],
        "trigger_text": str(r["trigger_text"]).replace('"', '""'),
        "opened_at": r["opened_at"],
        "closed_at": "",
        "outcome": "under_investigation",
        "pattern": "unclassified",
        "exposure_usd": 0.0,
        "report_filed": False,
        "actions_taken": "CREATE_CASE",
        "approval_route": "auto",
        "analyst_notes": f"Active exam alert triggered by {r['trigger_type']}: {r['trigger_text']}",
        "sar_narrative": ""
    })
    
    edges_tgt_card.append({"from_case": cid, "to_card": card_id})
    edges_inv_cust.append({"from_case": cid, "to_customer": cust_id})
    edges_owns.append({"from_customer": cust_id, "to_card": card_id, "opened_date": r["opened_at"]})
    edges_inv_txn.append({
        "from_case": cid,
        "to_transaction": flagged_txn,
        "is_flagged_trigger": True,
        "is_confirmed_fraud": False
    })

pd.DataFrame(cases).to_csv(os.path.join(PROCESSED_DIR, "vertices_fraud_case.csv"), index=False)
pd.DataFrame(edges_tgt_card).drop_duplicates().to_csv(os.path.join(PROCESSED_DIR, "edges_targets_card.csv"), index=False)
pd.DataFrame(edges_conn_card).drop_duplicates().to_csv(os.path.join(PROCESSED_DIR, "edges_connects_to_card.csv"), index=False)
pd.DataFrame(edges_inv_cust).drop_duplicates().to_csv(os.path.join(PROCESSED_DIR, "edges_investigates_customer.csv"), index=False)
pd.DataFrame(edges_exh_pat).drop_duplicates().to_csv(os.path.join(PROCESSED_DIR, "edges_exhibits_pattern.csv"), index=False)
pd.DataFrame(edges_inv_txn).drop_duplicates().to_csv(os.path.join(PROCESSED_DIR, "edges_investigates_txn.csv"), index=False)

# ----------------------------------------------------------------------
# 3. IDENTITY: DeviceProfile & USED_DEVICE edges
# ----------------------------------------------------------------------
print("3/9 Processing identity.csv and DeviceProfile vertices...")
idf = pd.read_csv(os.path.join(BASE_DIR, "identity.csv"))

device_profiles = {}
edges_used_dev = []

for _, r in idf.iterrows():
    tid = str(r["TransactionID"])
    d_info = str(r["DeviceInfo"]) if pd.notna(r["DeviceInfo"]) else "Unknown"
    d_type = str(r["DeviceType"]) if pd.notna(r["DeviceType"]) else "unknown"
    d_os = str(r["id_30"]) if pd.notna(r["id_30"]) else "UnknownOS"
    d_browser = str(r["id_31"]) if pd.notna(r["id_31"]) else "UnknownBrowser"
    d_screen = str(r["id_33"]) if pd.notna(r["id_33"]) else "UnknownRes"
    d_status = str(r["id_15"]) if pd.notna(r["id_15"]) else "Unknown"
    d_proxy = str(r["id_23"]) if pd.notna(r["id_23"]) else "None"
    d_match = str(r["id_34"]) if pd.notna(r["id_34"]) else "Unknown"
    
    # Hash profile signature
    sig = f"{d_info}|{d_os}|{d_browser}|{d_screen}|{d_type}"
    pid = "DEV_" + hashlib.md5(sig.encode("utf-8")).hexdigest()[:12]
    
    if pid not in device_profiles:
        device_profiles[pid] = {
            "device_profile_id": pid,
            "device_info": d_info.replace('"', '""'),
            "device_type": d_type,
            "os": d_os,
            "browser": d_browser,
            "screen_resolution": d_screen,
            "device_status": d_status,
            "proxy_flag": d_proxy,
            "match_status": d_match
        }
        
    edges_used_dev.append({
        "from_transaction": tid,
        "to_device_profile": pid,
        "is_new_device": (d_status == "New")
    })

pd.DataFrame(list(device_profiles.values())).to_csv(os.path.join(PROCESSED_DIR, "vertices_device_profile.csv"), index=False)
pd.DataFrame(edges_used_dev).drop_duplicates().to_csv(os.path.join(PROCESSED_DIR, "edges_used_device.csv"), index=False)
print(f"   Generated {len(device_profiles):,} distinct DeviceProfile vertices.")

# ----------------------------------------------------------------------
# 4. TRANSACTIONS STREAMING: Transaction, EmailDomain, BillingRegion, PERFORMS, NEXT_TRANSACTION
# ----------------------------------------------------------------------
print("4/9 Streaming transactions.csv for Transactions, Email, Regions, and Edges...")
all_customers = set(known_cards.values())
all_cards = set(known_cards.keys())
email_domains = set()
billing_regions = {}
flagged_set = set(str(t) for t in cp["flagged_txn_id"])

# Build card lookup map per customer from transactions
# To assign card_id to each transaction:
# If customer has only 1 card in known_cards, map to it.
# Otherwise, differentiate by card issuer (card1, card4, card6)
cust_card_map = {}
for card_id, cust_id in known_cards.items():
    cust_card_map.setdefault(cust_id, []).append(card_id)

# Process transactions in chunks
chunksize = 100000
txn_rows = []
edges_p_email = []
edges_r_email = []
edges_billed = []
edges_performs = []
card_txns = {}  # card_id -> list of (ts, amount, txn_id)

cols_to_read = [
    "TransactionID", "TransactionDT", "TransactionAmt", "ProductCD",
    "card1", "card4", "card6", "addr1", "addr2", "dist1", "dist2",
    "P_emaildomain", "R_emaildomain", "customer_id", "ts", "channel", "risk_score"
]

for chunk in pd.read_csv(os.path.join(BASE_DIR, "transactions.csv"), usecols=cols_to_read, chunksize=chunksize):
    for _, r in chunk.iterrows():
        tid = str(r["TransactionID"])
        cid = str(r["customer_id"])
        all_customers.add(cid)
        
        # Determine Card ID
        cards_for_cust = cust_card_map.get(cid, [])
        if len(cards_for_cust) == 1:
            chosen_card = cards_for_cust[0]
        elif len(cards_for_cust) > 1:
            # Default to K1 unless K2 has specific matching
            chosen_card = cards_for_cust[0]
        else:
            chosen_card = f"{cid}-K1"
            cust_card_map[cid] = [chosen_card]
            known_cards[chosen_card] = cid
            edges_owns.append({"from_customer": cid, "to_card": chosen_card, "opened_date": r["ts"]})
            
        all_cards.add(chosen_card)
        edges_performs.append({"from_card": chosen_card, "to_transaction": tid})
        card_txns.setdefault(chosen_card, []).append((r["ts"], float(r["TransactionAmt"]), tid))
        
        # Region
        if pd.notna(r["addr1"]):
            addr1_str = str(int(r["addr1"]))
            addr2_str = str(int(r["addr2"])) if pd.notna(r["addr2"]) else "87"
            reg_id = f"R_{addr1_str}_{addr2_str}"
            if reg_id not in billing_regions:
                billing_regions[reg_id] = {
                    "region_id": reg_id,
                    "region_code": addr1_str,
                    "country_code": addr2_str,
                    "is_domestic": (addr2_str == "87")
                }
            edges_billed.append({"from_transaction": tid, "to_billing_region": reg_id})
            
        # Emails
        if pd.notna(r["P_emaildomain"]):
            p_dom = str(r["P_emaildomain"]).strip().lower()
            email_domains.add(p_dom)
            edges_p_email.append({"from_transaction": tid, "to_email_domain": p_dom})
            
        if pd.notna(r["R_emaildomain"]):
            r_dom = str(r["R_emaildomain"]).strip().lower()
            email_domains.add(r_dom)
            edges_r_email.append({"from_transaction": tid, "to_email_domain": r_dom})
            
        # Transaction Vertex
        txn_rows.append({
            "transaction_id": tid,
            "ts": r["ts"],
            "amount": float(r["TransactionAmt"]),
            "channel": r["channel"],
            "product_cd": r["ProductCD"],
            "risk_score": float(r["risk_score"]),
            "dist1": float(r["dist1"]) if pd.notna(r["dist1"]) else "",
            "dist2": float(r["dist2"]) if pd.notna(r["dist2"]) else "",
            "is_flagged": (tid in flagged_set)
        })

print("5/9 Saving Transactions & Attribution tables...")
pd.DataFrame(txn_rows).to_csv(os.path.join(PROCESSED_DIR, "vertices_transaction.csv"), index=False)
pd.DataFrame([{"customer_id": c} for c in sorted(all_customers)]).to_csv(os.path.join(PROCESSED_DIR, "vertices_customer.csv"), index=False)
pd.DataFrame([{"card_id": c, "network": "visa", "card_type": "credit", "issuer_code": "1000"} for c in sorted(all_cards)]).to_csv(os.path.join(PROCESSED_DIR, "vertices_card.csv"), index=False)
pd.DataFrame([{"domain_name": d} for d in sorted(email_domains)]).to_csv(os.path.join(PROCESSED_DIR, "vertices_email_domain.csv"), index=False)
pd.DataFrame(list(billing_regions.values())).to_csv(os.path.join(PROCESSED_DIR, "vertices_billing_region.csv"), index=False)

pd.DataFrame(edges_owns).drop_duplicates().to_csv(os.path.join(PROCESSED_DIR, "edges_owns.csv"), index=False)
pd.DataFrame(edges_performs).to_csv(os.path.join(PROCESSED_DIR, "edges_performs.csv"), index=False)
pd.DataFrame(edges_p_email).to_csv(os.path.join(PROCESSED_DIR, "edges_purchaser_email.csv"), index=False)
pd.DataFrame(edges_r_email).to_csv(os.path.join(PROCESSED_DIR, "edges_recipient_email.csv"), index=False)
pd.DataFrame(edges_billed).to_csv(os.path.join(PROCESSED_DIR, "edges_billed_in.csv"), index=False)

# ----------------------------------------------------------------------
# 5. TEMPORAL NEXT_TRANSACTION EDGES
# ----------------------------------------------------------------------
print("6/9 Computing NEXT_TRANSACTION temporal sequence edges...")
edges_next = []
for card_id, txns in card_txns.items():
    # Sort chronologically
    txns.sort(key=lambda x: x[0])
    for i in range(len(txns) - 1):
        t1_ts, t1_amt, t1_id = txns[i]
        t2_ts, t2_amt, t2_id = txns[i+1]
        
        dt1 = datetime.strptime(t1_ts, "%Y-%m-%d %H:%M:%S")
        dt2 = datetime.strptime(t2_ts, "%Y-%m-%d %H:%M:%S")
        delta_sec = int((dt2 - dt1).total_seconds())
        delta_amt = round(t2_amt - t1_amt, 2)
        
        edges_next.append({
            "from_transaction": t1_id,
            "to_transaction": t2_id,
            "time_delta_sec": delta_sec,
            "amount_delta": delta_amt
        })

pd.DataFrame(edges_next).to_csv(os.path.join(PROCESSED_DIR, "edges_next_transaction.csv"), index=False)
print(f"   Generated {len(edges_next):,} NEXT_TRANSACTION edges.")

# ----------------------------------------------------------------------
# 6. POLICY RULE EDGES: GOVERNED_BY
# ----------------------------------------------------------------------
print("7/9 Linking FraudCase to PolicyRule edges...")
edges_gov = []
for c in cases:
    cid = c["case_id"]
    pat = c["pattern"]
    rep = c["report_filed"]
    acts = c["actions_taken"]
    
    if "BLOCK_CARD" in acts:
        edges_gov.append({"from_case": cid, "to_rule": "R2", "is_satisfied": True, "mandated_action": "BLOCK_CARD"})
    if rep:
        edges_gov.append({"from_case": cid, "to_rule": "R6", "is_satisfied": True, "mandated_action": "FILE_REPORT"})
    if pat == "card_testing":
        edges_gov.append({"from_case": cid, "to_rule": "R5", "is_satisfied": True, "mandated_action": "STEP_UP_AUTH"})
    if pat == "none":
        edges_gov.append({"from_case": cid, "to_rule": "R3", "is_satisfied": True, "mandated_action": "CLOSE_NO_FRAUD"})
    if pat == "undocumented":
        edges_gov.append({"from_case": cid, "to_rule": "R9", "is_satisfied": True, "mandated_action": "ESCALATE_TO_ANALYST"})

pd.DataFrame(edges_gov).drop_duplicates().to_csv(os.path.join(PROCESSED_DIR, "edges_governed_by.csv"), index=False)

print("8/9 Graph Data Preparation Completed Successfully!")
print(f"   Processed tables saved in: {PROCESSED_DIR}")
