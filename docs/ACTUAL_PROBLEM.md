# HHGOA — Actual Problem

## Core Problem

The project must investigate suspicious financial transactions and determine whether they are connected to other suspicious entities, why the activity is risky, what evidence supports the assessment, and what action should be taken.

## Why This Is Difficult

A suspicious transaction cannot always be evaluated in isolation.

Relevant evidence may be distributed across:

- Customers
- Accounts
- Transactions
- Devices
- Merchants
- Identity relationships
- Historical investigations
- Previous fraud patterns

The investigator therefore needs to discover relationships and patterns across these entities.

## Core Investigation Flow

Trigger
→ Investigate
→ Gather Evidence
→ Assess Risk and Uncertainty
→ Gather Additional Evidence if Required
→ Determine Next Best Action
→ Explain Decision
→ Update Case Memory

## Expected Agent Behavior

The agent should:

1. Receive a fraud signal, risk score, customer report, or analyst trigger.
2. Investigate the relevant customer, account, transaction, device, merchant, and related entities.
3. Identify suspicious relationships and fraud patterns.
4. Use historical cases and case memory when relevant.
5. Determine whether enough evidence exists.
6. Request additional evidence when necessary.
7. Recommend or execute an approved action according to policy and permissions.
8. Explain the evidence, uncertainty, reasoning, and recommended action.
9. Update the investigation/case with findings and decisions.

## Example

A transaction may initially appear normal:

Customer → Account → Transaction → Merchant

Graph investigation may reveal:

Customer A
→ Account A
→ Transaction
→ Device D
→ Customer B
→ Account B
→ Multiple related transactions

The relationship between these entities may provide additional evidence for the investigation.

## Role of TigerGraph

TigerGraph is used to represent and investigate relationships between fraud-related entities.

The graph enables traversal and pattern analysis across:

Customer → Account → Transaction → Merchant
Customer → Device → Account
Customer → Historical Case
Transaction → Related Entities

The purpose is not simply to store transactions, but to support relationship-based investigation.

## Final Objective

Build an agentic fraud-investigation system that can move from:

Fraud Signal

to

Evidence

to

Risk Assessment

to

Next Best Action

to

Explainable Case Update

while operating within defined policies and permissions.