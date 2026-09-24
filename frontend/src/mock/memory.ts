// HHGOA Mock Case Memory Data
// DEMO DATA — TigerGraph offline. Replace with real backend when available.

import type { CaseMemory, SimilarCase, Decision, Action } from '@/types';

export const similarCases: SimilarCase[] = [
  {
    id: 'CASE-0003',
    similarity: 0.78,
    matchingEntities: ['CUST-1024', 'DEV-9F3A'],
    matchingPatterns: ['Rapid transaction velocity', 'Device reuse'],
    outcome: 'Confirmed fraud',
  },
  {
    id: 'CASE-0007',
    similarity: 0.65,
    matchingEntities: ['DEV-9F3A', 'CUST-2109'],
    matchingPatterns: ['Device reuse', 'Linked suspicious entities'],
    outcome: 'Confirmed fraud',
  },
  {
    id: 'CASE-0009',
    similarity: 0.54,
    matchingEntities: ['CUST-2109', 'DEV-9F3A'],
    matchingPatterns: ['Device reuse'],
    outcome: 'Escalated',
  },
];

export const previousDecisions: Decision[] = [
  {
    id: 'DEC-0001',
    caseId: 'CASE-0001',
    action: 'Step-up authentication required',
    reason: 'Velocity pattern detected but device is known',
    timestamp: '2026-09-20T10:00:00Z',
    approvedBy: 'System Agent',
  },
  {
    id: 'DEC-0002',
    caseId: 'CASE-0003',
    action: 'Close case — no fraud',
    reason: 'Customer confirmed travel',
    timestamp: '2026-09-12T08:00:00Z',
    approvedBy: 'Analyst B. Patel',
  },
];

export const previousActions: Action[] = [
  {
    id: 'ACT-0001',
    caseId: 'CASE-0001',
    type: 'approve',
    target: 'STEP_UP_AUTH',
    note: 'Requested step-up authentication',
    timestamp: '2026-09-20T10:00:00Z',
    performedBy: 'System Agent',
  },
  {
    id: 'ACT-0002',
    caseId: 'CASE-0003',
    type: 'approve',
    target: 'CLOSE_NO_FRAUD',
    note: 'Case closed — no fraud detected',
    timestamp: '2026-09-12T08:00:00Z',
    performedBy: 'Analyst B. Patel',
  },
];

export const recurringEntities = ['CUST-1024', 'CUST-2109', 'DEV-9F3A'];
export const recurringDevices = ['DEV-9F3A', 'DEV-NEW-7742'];
export const recurringMerchants = ['Online Electronics', 'Test Merchant'];
export const historicalOutcomes = ['Confirmed fraud', 'Escalated', 'Cleared'];

export const caseMemory: CaseMemory = {
  similarCases,
  previousDecisions,
  previousActions,
  recurringEntities,
  recurringDevices,
  recurringMerchants,
  historicalOutcomes,
};

export function getCaseMemory(caseId?: string): Promise<CaseMemory> {
  return Promise.resolve(caseMemory);
}

export function getSimilarCases(caseId: string): Promise<SimilarCase[]> {
  return Promise.resolve(similarCases);
}