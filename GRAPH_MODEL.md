# TigerGraph Graph Model

## Purpose
Represent customers, accounts, transactions, devices, identities, cases, evidence, actions, and their relationships for connected fraud investigation.

## Candidate vertex types
Customer, Account, Transaction, Device, Identity, Connection, FraudCase, Evidence, Action, EvidenceRequest.

## Candidate edge types
OWNS, MADE, USES, LINKED_TO, CONNECTED_TO, INVOLVES, HAS_EVIDENCE, RESULTED_IN, REQUESTED, SIMILAR_TO, RELATED_TO.

## GSQL responsibilities
- Multi-hop traversal
- Shared-device analysis
- Connected-account discovery
- Transaction relationship analysis
- Historical-case retrieval
- Fraud-pattern detection
- Relevant evidence retrieval

## Important
Do not finalize schema field names until the HHGOA_IEEE README has been read and the actual dataset columns have been inspected.
