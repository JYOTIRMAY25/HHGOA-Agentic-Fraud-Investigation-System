# HHGOA IEEE-CIS Fraud Detection Dataset Audit
**Authoritative Phase 1 Audit Report**

---

## 1. Executive Summary & Inventory

This dataset audit provides a rigorous, empirical verification of the four data files in the **TigerGraph × Hacker House Goa — Fraud Investigation Dataset (IEEE-CIS edition)**.

| File Name | File Size | Row Count | Column Count | Primary Key / Join Key | Purpose |
|---|---|---|---|---|---|
| 	ransactions.csv | ~708 MB (707,936,515 bytes) | 590,742 | 397 | TransactionID | Complete card transaction history with synthetic timestamps, customer IDs, and model risk scores |
| identity.csv | ~26.7 MB (26,716,154 bytes) | 144,432 | 41 | TransactionID | Device network and browser identity features for online transactions |
| closed_cases_history.csv | ~2.7 MB (2,706,417 bytes) | 5,565 | 15 | case_id | Historical closed bank investigations (July to October 2016) with ground truth outcomes and notes |
| case_pack.csv | ~3.5 KB (3,548 bytes) | 20 | 8 | case_id | 20 exam investigation targets (November to December 2016) with trigger details |

---

## 2. Referential Integrity & Key Relationships

An exhaustive foreign-key cross-validation confirms **100% referential integrity** across the entire dataset:

- **Case Pack Flagged Transactions:** All 20 flagged transactions (100%) exist in 	ransactions.csv.
- **Case Pack Customers:** All 20 customers (100%) exist in 	ransactions.csv.
- **Closed Case Transactions:** All 14,955 distinct transaction IDs referenced in closed_cases_history.csv (100%) exist in 	ransactions.csv (0 missing).
- **Closed Case Customers:** All 1,892 distinct customer IDs in closed_cases_history.csv (100%) exist in 	ransactions.csv (0 missing).
- **Identity Records:** All 144,432 identity records (100%) join to online transactions in 	ransactions.csv via TransactionID with zero dangling records.
- **Connected Cards:** All 24 connected card IDs referenced in closed_cases_history.csv belong to valid customer prefixes present in the dataset.
- **Case Memory Precedent:** 16 of the 20 case pack customers (80%) have prior investigations recorded in closed_cases_history.csv.

---

## 3. Dataset Characteristics & Column Distributions

### Temporal Dimensions
- **Transaction Window:** Spans 6 months from 2016-07-02 00:00:09 to 2016-12-31 23:59:08.
- **Closed Cases Window:** Historical investigations opened from 2016-07-02 07:17:26 to 2016-11-02 02:00:37, and closed between 2016-07-04 and 2016-11-06.
- **Case Pack Window:** Exam alerts opened from 2016-11-12 00:46:24 to 2016-12-29 07:53:54.

### Transaction Amounts & Channels
- **Transaction Amounts:** Minimum: .251, Maximum: ,937.39, Mean: .03. No negative or zero amounts.
- **Channels & Product Codes:**
  - in_person: 439,670 transactions (74.43%), corresponding exactly to ProductCD = W. In-person transactions have no identity record.
  - online: 151,072 transactions (25.57%), corresponding to ProductCD in {'C': 68,721, 'R': 37,699, 'H': 33,024, 'S': 11,628}. Identity records join to online transactions.

### Risk Scores & Fraud Labels
- **Model Risk Score:** Continuous value in [0.0, 1.0], mean 0.1691. 0 null values in 	ransactions.csv.
- **CRITICAL AUDIT FACT:** There is **NO isFraud column** in 	ransactions.csv. The model risk score is an input signal, NOT ground truth. Above 0.70, many flagged transactions are legitimate, and some fraud scores near zero. Ground truth exists solely in closed_cases_history.csv.

### Identity & Device Fingerprints
- **Device Info:** 1,786 distinct device info strings (e.g. SAMSUNG SM-G935F, iOS Device, Windows, MacOS).
- **Key Categorical Identity Fields:**
  - DeviceType: desktop (85,165), mobile (55,645).
  - id_15 (Device Status): Found (67,985), New (61,614).
  - id_23 (Proxy Flag): IP_PROXY:TRANSPARENT (3,397), IP_PROXY:ANONYMOUS (1,071), IP_PROXY:HIDDEN (169).
  - id_30 (Operating System): 75 distinct OS values (e.g., Windows 10, Android 7.0, iOS 11.1.2).
  - id_31 (Browser): 130 distinct browser strings (e.g., chrome 63.0, mobile safari 11.0).
  - id_33 (Screen Resolution): 260 distinct screen resolutions (e.g., 1920x1080, 2220x1080).

### Geography & Network Identifiers
- **Billing Regions:** ddr1 contains 332 distinct regional codes. ddr2 contains country codes, where 87.0 is the domestic home country (520,643 occurrences).
- **Email Domains:** P_emaildomain has 59 distinct domains (top: gmail.com 228,436, yahoo.com 100,969). R_emaildomain has 60 distinct domains.

---

## 4. Ground Truth Case Patterns (from closed_cases_history.csv)

Ground truth patterns across the 5,565 closed investigations:
- card_not_present_fraud: 1,404 cases (25.23%)
- ccount_takeover: 1,205 cases (21.65%)
- card_not_present_new_device: 1,076 cases (19.33%)
- out_of_region_use: 955 cases (17.16%)
- 
one (Cleared / False Alarm): 900 cases (16.17%)
- card_testing: 16 cases (0.29%)
- undocumented: 9 cases (0.16%)

Outcomes:
- confirmed_fraud: 4,665 (83.83%)
- cleared: 900 (16.17%)
- SAR 
eport_filed = Yes: 397 cases (all confirmed fraud with exposure or shared ring connections).

---

## 5. Separation of Facts vs Inferred vs Proposed

### Confirmed Dataset Facts
- Explicit schemas, column names, and row counts across all 4 files.
- 	ransactions.csv joins to identity.csv on TransactionID (for online transactions).
- closed_cases_history.csv and case_pack.csv contain case_id, customer_id, card_id, and transaction IDs that 100% match 	ransactions.csv.
- Absence of isFraud column in transactions.

### Inferred Relationships
- Card: Cards are identified in cases as <customer_id>-<suffix> (e.g., C12382-K1, C08623-K2). In 	ransactions.csv, a card is defined by customer ownership combined with issuer parameters (card1 to card6).
- DeviceProfile: An online device identity composite formed by DeviceInfo + id_30 (OS) + id_31 (browser) + id_33 (screen resolution) + DeviceType.

### Proposed Graph Design Decisions
- Direct vertex representations for Customer, Card, Transaction, DeviceProfile, EmailDomain, and BillingRegion.
- Dynamic and historical case memory modeling via a unified FraudCase vertex.
- Knowledge vertices for FraudPattern and PolicyRule to support deterministic policy reasoning and GraphRAG.
- Edges modeling structural ownership (OWNS), transaction execution (PERFORMS), temporal chaining (NEXT_TRANSACTION), contextual attribution (USED_DEVICE, BILLED_IN, PURCHASER_EMAIL, RECIPIENT_EMAIL), case scope (INVESTIGATES_TXN, ON_CARD, CONNECTED_CARD), and knowledge grounding (EXHIBITS_PATTERN, GOVERNED_BY).
