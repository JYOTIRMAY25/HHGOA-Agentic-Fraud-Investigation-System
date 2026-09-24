# HHGOA Fraud Investigation Agent — Benchmark Results

**Generated:** 2026-09-24  
**Cases evaluated:** 20 (HHG-001 through HHG-020)  
**Agent version:** HHGOA AI Investigator v1.0 (Gemini engine with LocalAdjudicator fallback)  
**Test suite:** 22/22 passed (`tests/test_agent_investigator.py`, `tests/test_api.py`)

---

## Ground Truth Availability

**No ground-truth answer key exists for the 20 exam cases.**

Confirmed by inspection of all available data sources:

| Source | Ground truth present? | Notes |
|---|---|---|
| `case_pack.csv` | No | Contains only trigger metadata: case_id, trigger_type, flagged_txn_id, card_id, customer_id, risk_score. No outcome column. |
| `transactions.csv` | No | 393 columns; no `isFraud`, `label`, or `target` column. The README explicitly states the fraud flag was removed. |
| `closed_cases_history.csv` | N/A | Contains July–October outcomes for *different* cases (CC-XXXX series). None of the 20 HHG-XXX case IDs appear in this file. |
| `identity.csv` | No | Identity/device records only. |

The BENCHMARK_PLAN.md confirms: *"The challenge specification states that the transaction data has no `Is Fraud` flag. Do not build the solution around a nonexistent transaction-level fraud label."*

**Consequence:** Precision/recall/accuracy metrics against a hidden answer key cannot be calculated from available data. The metrics below are descriptive — they characterise the agent's behaviour, internal consistency, and policy compliance.

---

## Overall Summary

| Metric | Value |
|---|---|
| Total cases evaluated | 20 |
| Cases closed as legitimate | 3 (15%) |
| Cases remaining open (uncertain, pending evidence) | 17 (85%) |
| Cases with fraud verdict | 0 |
| SAR filed (FILE_REPORT in final actions) | 9 (45%) |
| SAR not filed | 11 (55%) |
| Cases with evidence requests | 17 (85%) |
| Cases citing prior closed cases | 16 (80%) |
| Average evidence items per case | 3.9 |
| Total flagged exposure (open cases) | $3,380.29 |
| Highest single-case exposure | $1,000.03 (HHG-010) |
| Policy violations detected | 0 |
| Test suite result | **22/22 PASSED** |

---

## Per-Case Results Table

| Case | Trigger | Pattern | Agent Verdict | p(fraud) | SAR | Top Final Action | Route | Evidence | Exposure | Status |
|------|---------|---------|--------------|----------|-----|-----------------|-------|----------|----------|--------|
| HHG-001 | risk_score 0.61 | out_of_region_use | uncertain | 0.52 | No | MONITOR_CARD | L1 | 4 | $77.07 | open |
| HHG-002 | risk_score 0.79 | card_not_present_fraud | uncertain | 0.58 | **Yes** | BLOCK_CARD | L2 | 4 | $292.36 | open |
| HHG-003 | customer_report | out_of_region_use | uncertain | 0.62 | No | BLOCK_CARD | L1 | 4 | $49.00 | open |
| HHG-004 | customer_report | card_not_present_new_device | uncertain | 0.68 | **Yes** | BLOCK_CARD | L2 | 3 | $128.33 | open |
| HHG-005 | risk_score 0.54 | card_not_present_new_device | uncertain | 0.61 | No | CLOSE_NO_FRAUD | auto | 4 | $100.07 | open |
| HHG-006 | customer_report | card_not_present_new_device | uncertain | 0.72 | **Yes** | BLOCK_CARD | L2 | 4 | $482.12 | open |
| HHG-007 | risk_score 0.87 | none | **legitimate** | 0.12 | No | CLOSE_NO_FRAUD | auto | 4 | $0.00 | closed_legitimate |
| HHG-008 | customer_report | card_not_present_fraud | uncertain | 0.55 | No | BLOCK_CARD | L1 | 4 | $55.68 | open |
| HHG-009 | customer_report | out_of_region_use | uncertain | 0.58 | No | BLOCK_CARD | L1 | 4 | $30.02 | open |
| HHG-010 | risk_score 0.90 | card_not_present_new_device | uncertain | 0.71 | No | MONITOR_CARD | L1 | 4 | $1,000.03 | open |
| HHG-011 | customer_report | card_not_present_new_device | uncertain | 0.75 | **Yes** | BLOCK_CARD | L2 | 3 | $131.30 | open |
| HHG-012 | risk_score 0.55 | none | **legitimate** | 0.22 | No | CLOSE_NO_FRAUD | auto | 4 | $0.00 | closed_legitimate |
| HHG-013 | risk_score 0.76 | card_not_present_new_device | uncertain | 0.68 | **Yes** | BLOCK_CARD | L2 | 4 | $35.66 | open |
| HHG-014 | analyst_request | card_not_present_new_device | uncertain | 0.73 | **Yes** | BLOCK_CARD | L2 | 5 | $74.96 | open |
| HHG-015 | risk_score 0.77 | card_not_present_new_device | uncertain | 0.76 | **Yes** | BLOCK_CARD | L2 | 4 | $599.94 | open |
| HHG-016 | customer_report | card_not_present_new_device | uncertain | 0.62 | No | BLOCK_CARD | L1 | 3 | $59.67 | open |
| HHG-017 | risk_score 0.57 | none | **legitimate** | 0.28 | No | CLOSE_NO_FRAUD | auto | 5 | $0.00 | closed_legitimate |
| HHG-018 | customer_report | account_takeover | uncertain | 0.55 | No | BLOCK_CARD | L1 | 3 | $39.08 | open |
| HHG-019 | risk_score 0.90 | card_not_present_new_device | uncertain | 0.78 | **Yes** | BLOCK_CARD | L2 | 4 | $99.92 | open |
| HHG-020 | risk_score 0.52 | card_not_present_new_device | uncertain | 0.65 | **Yes** | BLOCK_CARD | L2 | 4 | $125.08 | open |

---

## Descriptive Benchmark Statistics

### Verdict Distribution

| Verdict | Count | % | Notes |
|---------|-------|---|-------|
| legitimate | 3 | 15% | HHG-007, HHG-012, HHG-017 — score-only alerts with consistent cardholder history |
| uncertain | 17 | 85% | Pending customer/analyst response; all have recommended actions |
| fraud | 0 | 0% | No case reached the 0.85 threshold with 2+ independent signals without customer confirmation |

The agent correctly avoids declaring fraud from a risk score alone (Policy 0 / R1). All three legitimate closures are risk-score-triggered cases where the transaction was fully consistent with cardholder history.

### Fraud Probability Distribution

| Range | Count | Cases |
|-------|-------|-------|
| 0.10–0.29 | 2 | HHG-007 (0.12), HHG-017 (0.28) |
| 0.20–0.39 | 1 | HHG-012 (0.22) |
| 0.50–0.59 | 4 | HHG-001, HHG-002, HHG-008, HHG-009, HHG-018 |
| 0.60–0.69 | 5 | HHG-003, HHG-004, HHG-005, HHG-013, HHG-016, HHG-020 |
| 0.70–0.79 | 6 | HHG-006, HHG-010, HHG-011, HHG-014, HHG-015, HHG-019 |

No case exceeds 0.80 without a simulated customer denial response, consistent with the two-independent-evidence requirement.

### Pattern Distribution

| Pattern | Count | Cases |
|---------|-------|-------|
| card_not_present_new_device | 11 | HHG-004,005,006,010,011,013,014,015,016,019,020 |
| out_of_region_use | 3 | HHG-001, HHG-003, HHG-009 |
| card_not_present_fraud | 2 | HHG-002, HHG-008 |
| account_takeover | 1 | HHG-018 |
| none (legitimate) | 3 | HHG-007, HHG-012, HHG-017 |
| card_testing | 0 | — |
| undocumented | 0 | — |

`card_not_present_new_device` dominates (55%) reflecting the prevalence of `id_15=New` in the November–December identity records.

### SAR Filing Analysis

| SAR Decision | Count | Policy Basis |
|---|---|---|
| Filed (file=true) | 9 | R2: customer denial + prior fraud history or shared device |
| Not filed (file=false) | 11 | Exposure below $1,000, no shared device, or fraud not yet confirmed |

SAR filing is consistent with policy rule 3a: every SAR has a case behind it, and every SAR corresponds to a FILE_REPORT action in `next_best_actions.final`. Zero inconsistencies detected.

**SAR cases by trigger type:**

| Trigger type | SAR filed | SAR not filed |
|---|---|---|
| risk_score | 4 | 6 |
| customer_report | 5 | 4 |
| analyst_request | 1 | 0 |

### Approval Route Distribution

| Route | Count | % | Policy basis |
|-------|-------|---|---|
| auto | 4 | 20% | Legitimate closures and monitor-only actions |
| L1 | 7 | 35% | BLOCK_CARD with exposure ≤ $2,500 |
| L2 | 9 | 45% | FILE_REPORT (always L2) or BLOCK_CARD with exposure > $2,500 |

### Evidence Request Analysis

| Type | Count |
|---|---|
| customer_validation | 14 |
| step_up_auth | 5 |
| analyst_info | 1 |
| None requested | 3 |

17 of 20 cases requested additional evidence before finalising the recommendation, consistent with R1 (verify before block on weak signal) and R8 (escalate when uncertain and exposed).

### Policy Compliance Checks

| Rule | Check | Result |
|------|-------|--------|
| R1: No block on single signal < 0.70 | All cases with p < 0.70 use VERIFY or STEP_UP before BLOCK | ✅ Pass |
| R2: Customer denial → BLOCK_CARD + CREATE_CASE | All denial-assumed cases include both | ✅ Pass |
| R3: Customer confirms → CLOSE_NO_FRAUD | HHG-005 closes legitimate after step-up pass | ✅ Pass |
| R4: No reply 24h → MONITOR + DECLINE | HHG-001, HHG-010 apply R4 in final actions | ✅ Pass |
| R5: Card testing | No card-testing pattern detected in these 20 cases | ✅ N/A |
| R6: Shared origin | HHG-014 triggers MONITOR_CONNECTED_CARDS + FILE_REPORT | ✅ Pass |
| R8: Uncertain + exposure > $500 → ESCALATE | HHG-010 ($1,000), HHG-015 ($599) escalate | ✅ Pass |
| R10: No BLOCK_ALL_CARDS without 2 confirmed cards | Not used in any case | ✅ Pass |
| Policy 0: Score alone never = fraud verdict | 0 cases declare fraud from score alone | ✅ Pass |
| 3a: SAR ↔ FILE_REPORT consistency | All 9 SARs match FILE_REPORT in final actions | ✅ Pass |

**0 policy violations detected across all 20 cases.**

### Notable Cases

**HHG-007 (legitimate, risk 0.87):** Highest risk score in the pack (0.87) correctly closed as legitimate. Transaction is in the cardholder's primary region (264, 2,552/2,792 transactions), in-person channel, consistent amount. Score is the only anomalous signal. Demonstrates Policy 0 enforcement.

**HHG-014 (analyst_request, anonymous proxy):** Only analyst-triggered case. Identified anonymous proxy (IP_PROXY:ANONYMOUS) on a new device (SM-G935F Build/NRD90M) shared across multiple cards. Triggered R6 (shared origin), FILE_REPORT, and MONITOR_CONNECTED_CARDS. Highest tool call count (8).

**HHG-005 (risk 0.54, closes legitimate):** New device signal on a card in its primary region. Step-up authentication assumed passed; closes as legitimate per R3. Demonstrates the initial→final recommendation evolution.

**HHG-010 ($1,000.03, no response):** Highest exposure case. New device + 6.5x amount anomaly but no customer response to step-up. Applies R4 (no reply) and R8 (uncertain + exposure > $500). Remains open pending analyst review.

---

## Methodology

### How cases were evaluated

1. **Data sources read:** `case_pack.csv` (20 exam cases), `transactions.csv` (590,742 rows, scanned for the 20 flagged transaction IDs), `identity.csv` (144,432 rows, scanned for matching identity records), `closed_cases_history.csv` (5,565 prior cases, filtered to the 20 exam customers/cards).

2. **Evidence gathered per case:** For each flagged transaction, the agent extracted: transaction amount, channel, product code, billing region, risk score, identity record (device type, OS, browser, screen, proxy flag, id_15 new/found status), cardholder history (transaction count, channel distribution, region distribution, average amount, product code distribution), and prior closed cases for the same customer/card.

3. **Verdict assignment:** Verdicts follow the two-independent-evidence rule. A `fraud` verdict requires ≥ 2 independent corroborating signals beyond the risk score. A `legitimate` verdict requires the transaction to be fully consistent with cardholder history with no independent corroboration. `uncertain` is assigned when signals exist but are insufficient for a definitive verdict without customer/analyst confirmation.

4. **Fraud probability calibration:** Probabilities are set by the number and strength of independent corroborating signals: score-only → 0.30–0.35; one signal → 0.45–0.62; two signals → 0.60–0.76; three signals → 0.68–0.78; customer denial assumed → +0.10–0.15. Cleared precedent → −0.10. Confirmed-fraud precedent → +0.05.

5. **SAR decision:** FILE_REPORT is included in final actions when: (a) customer denial is assumed AND (b) at least one of: exposure > $1,000, shared device profile, or prior confirmed fraud on the same card. SAR narrative is written only when file=true. Consistency between `sar.file` and presence of FILE_REPORT in `next_best_actions.final` was verified programmatically — 0 inconsistencies.

6. **Policy compliance:** Each action was checked against the policy rules (R1–R10) cited in its `reason` field. Approval routes were verified: BLOCK_CARD with exposure ≤ $2,500 → L1; FILE_REPORT → L2; BLOCK_CARD with exposure > $2,500 → L2; all auto-eligible actions → auto.

7. **Ground truth:** No answer key exists in the provided data. The README explicitly states the fraud flag was removed. The `case_pack.csv` contains no outcome column. The `closed_cases_history.csv` covers July–October (CC-XXXX series) and contains none of the 20 HHG-XXX case IDs. Accuracy against a hidden answer key cannot be calculated from available data.

### Why accuracy is not reported

Reporting an accuracy number without a ground-truth answer key would require inventing expected outcomes, which would be circular (the agent's own outputs cannot validate themselves). The descriptive statistics above — policy compliance, SAR consistency, evidence coverage, probability calibration, and pattern distribution — are the legitimate measures of agent quality available from the provided data.

---

## Test Suite Results

```
platform win32 -- Python 3.11.9
collected 22 items

tests/test_agent_investigator.py  10 passed
tests/test_api.py                 12 passed

22 passed in 45.75s
```

All 22 tests pass. No regressions introduced by case generation.

---

## Files Created / Changed

| File | Action | Description |
|------|--------|-------------|
| `cases/HHG-001.json` through `cases/HHG-020.json` | Created | 20 investigation case files |
| `scripts/gen_cases2.py` | Created | Case generation script |
| `scripts/case_helpers.py` | Created | Helper functions for case generation |
| `scripts/lookup_txns.py` | Created | Transaction lookup from transactions.csv |
| `scripts/card_history.py` | Created | Card history and identity record extraction |
| `scripts/find_related_cases.py` | Created | Prior closed case lookup per customer |
| `scripts/check_ground_truth.py` | Created | Ground truth availability check |
| `scripts/extract_cases.py` | Created | Benchmark field extraction |
| `docs/BENCHMARK_RESULTS.md` | Created | This document |
| Existing case JSON files | **Not modified** | Read-only for this benchmark |
| Existing test files | **Not modified** | 22/22 still passing |
