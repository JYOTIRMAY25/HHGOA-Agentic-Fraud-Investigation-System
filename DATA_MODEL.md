# Data Model

> Final fields must be mapped from the HHGOA_IEEE README and actual dataset files.

## Candidate entities
- Customer
- Account
- Transaction
- Device
- Identity
- Connection
- FraudCase
- Evidence
- Action
- EvidenceRequest

## Candidate relationships
- Customer OWNS Account
- Account MADE Transaction
- Account USES Device
- Device LINKED_TO Account
- Customer HAS Identity
- Transaction INVOLVES Case
- Case HAS_EVIDENCE Evidence
- Case RESULTED_IN Action
- Case REQUESTED EvidenceRequest
- Case SIMILAR_TO Case
- Case INVOLVES Account

## Case fields
- case_id
- trigger
- status
- risk_assessment
- confidence
- findings
- evidence
- decisions
- actions
- approvals
- outcome

## Evidence fields
- evidence_id
- case_id
- source
- entity/transaction reference
- finding
- relevance
- timestamp
- evidence_type
