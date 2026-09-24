// HHGOA Mock Agent Assessment Data
// DEMO DATA — TigerGraph offline. Replace with real backend when available.

import type { AgentAssessment, Action, FraudPattern, EvidenceRequest } from '@/types';

export const demoPatterns: FraudPattern[] = [
  {
    id: 'PAT-001',
    name: 'Rapid transaction velocity',
    severity: 'high',
    confidence: 'high',
    supportingEvidenceCount: 4,
    description: 'Multiple high-value transactions within a short time window, inconsistent with customer history.',
    relatedEntities: ['TXN-4850', 'TXN-4851', 'TXN-4852'],
    detectionSource: 'TigerGraph Query: detect_card_testing',
  },
  {
    id: 'PAT-002',
    name: 'Device reuse',
    severity: 'high',
    confidence: 'high',
    supportingEvidenceCount: 3,
    description: 'Same device profile associated with multiple customer accounts.',
    relatedEntities: ['DEV-9F3A', 'CUST-1024', 'CUST-2109'],
    detectionSource: 'TigerGraph Query: trace_connected_entities',
  },
  {
    id: 'PAT-003',
    name: 'Geographic inconsistency',
    severity: 'medium',
    confidence: 'medium',
    supportingEvidenceCount: 2,
    description: 'Billing region mismatch between transaction and customer history.',
    relatedEntities: ['TXN-4850'],
    detectionSource: 'TigerGraph Query: analyze_region_anomalies',
  },
];

export const demoAssessment: AgentAssessment = {
  investigationId: 'INV-0001',
  status: 'investigating',
  assessment: 'Potential coordinated account activity detected. Multiple transactions from a shared device profile across customer accounts.',
  riskAssessment: 'High risk — 87/100. Velocity pattern detected with device reuse signal.',
  confidence: 'medium',
  uncertainty: 'Customer ownership of the device requires validation. Identity confirmation is still needed.',
  evidenceFound: [
    '4 transaction signals',
    '2 device relationships',
    '1 historical case similarity',
    '1 geographic inconsistency',
  ],
  missingEvidence: [
    'Step-up customer verification',
    'Identity confirmation',
  ],
  nextBestAction: 'Request customer validation',
  policyRequirement: 'R1: Verify before block on weak signal',
  approvalRoute: 'L1',
  evidenceCount: 12,
  patternsDetected: demoPatterns,
  actionHistory: [
    {
      id: 'ACT-HIST-001',
      caseId: 'CASE-0001',
      type: 'approve',
      target: 'STEP_UP_AUTH',
      note: 'Requested step-up authentication',
      timestamp: '2026-09-20T10:00:00Z',
      performedBy: 'System Agent',
    },
  ],
  isDemo: true,
};

export function getAgentAssessment(investigationId: string): Promise<AgentAssessment> {
  return Promise.resolve({ ...demoAssessment, investigationId });
}

export function requestEvidence(
  investigationId: string,
  type: 'customer_validation' | 'step_up_auth' | 'analyst_info'
): Promise<EvidenceRequest> {
  return Promise.resolve({
    id: 'EVR-' + Date.now(),
    investigationId,
    type,
    requestedAt: new Date().toISOString(),
    status: 'pending',
    assumedResponse: 'Customer confirms they did not make this transaction.',
  });
}

export function approveAction(investigationId: string, actionId: string): Promise<Action> {
  return Promise.resolve({
    id: actionId,
    caseId: investigationId,
    type: 'approve',
    target: 'STEP_UP_AUTH',
    note: 'Action approved in demo mode',
    timestamp: new Date().toISOString(),
    performedBy: 'Analyst (Demo)',
  });
}

export function escalateInvestigation(investigationId: string): Promise<Action> {
  return Promise.resolve({
    id: 'ACT-ESC-' + Date.now(),
    caseId: investigationId,
    type: 'escalate',
    target: 'ESCALATE_TO_ANALYST',
    note: 'Escalated in demo mode',
    timestamp: new Date().toISOString(),
    performedBy: 'System Agent (Demo)',
  });
}