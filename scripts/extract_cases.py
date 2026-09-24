import json, glob, os

files = sorted(glob.glob(os.path.join(os.path.dirname(__file__), '..', 'cases', '*.json')))
rows = []
for f in files:
    d = json.load(open(f))
    c = d['case']
    nba = d['next_best_actions']
    sar = d['sar']
    final_actions = [a['action'] for a in nba['final']]
    initial_actions = [a['action'] for a in nba['initial']]
    routes = [a['route'] for a in nba['final']]
    top_route = max(routes, key=lambda x: {'auto':0,'L1':1,'L2':2}[x]) if routes else 'auto'
    rows.append({
        'case_id': d['case_id'],
        'verdict': c['verdict'],
        'fraud_probability': c['fraud_probability'],
        'pattern': c['pattern'],
        'status': c['status'],
        'sar_file': sar['file'],
        'sar_reason': sar['reason'],
        'final_actions': final_actions,
        'initial_actions': initial_actions,
        'top_final_action': final_actions[0] if final_actions else '',
        'approval_route': top_route,
        'evidence_count': len(c['evidence']),
        'exposure_usd': c['exposure_usd'],
        'prior_cases': c['similar_prior_cases'],
        'connected_cards': c['connected_card_ids'],
        'device_profiles': c['connected_device_profiles'],
        'affected_txns': c['affected_txn_ids'],
        'summary': c['summary'],
        'stop_reason': d['stop_reason'],
        'tool_calls': d['tool_calls'],
        'evidence_requests': d['evidence_requests'],
        'what_changed': nba['what_changed'],
    })

for r in rows:
    print(f"{r['case_id']} | verdict={r['verdict']} | p={r['fraud_probability']} | pattern={r['pattern']} | sar={r['sar_file']} | top_action={r['top_final_action']} | route={r['approval_route']} | ev={r['evidence_count']} | exp=${r['exposure_usd']} | status={r['status']}")

print(f"\nTotal cases: {len(rows)}")
print(f"Verdicts: { {v: sum(1 for r in rows if r['verdict']==v) for v in ['fraud','legitimate','uncertain']} }")
print(f"SAR filed: {sum(1 for r in rows if r['sar_file'])}")
print(f"SAR not filed: {sum(1 for r in rows if not r['sar_file'])}")
print(f"Patterns: { {p: sum(1 for r in rows if r['pattern']==p) for p in set(r['pattern'] for r in rows)} }")
print(f"Statuses: { {s: sum(1 for r in rows if r['status']==s) for s in set(r['status'] for r in rows)} }")
print(f"Routes: { {rt: sum(1 for r in rows if r['approval_route']==rt) for rt in ['auto','L1','L2']} }")
print(f"Total exposure flagged: ${sum(r['exposure_usd'] for r in rows):.2f}")
print(f"Avg evidence items: {sum(r['evidence_count'] for r in rows)/len(rows):.1f}")
print(f"Cases with evidence requests: {sum(1 for r in rows if r['evidence_requests'])}")
print(f"Cases with prior cases cited: {sum(1 for r in rows if r['prior_cases'])}")
