// HHGOA Mock Cases Data
// DEMO DATA — TigerGraph offline. Replace with real backend when available.

import type { Case, Evidence, Action, Decision, TimelineEvent, SimilarCase } from '@/types';

const NOW = '2026-09-20T11:00:00Z';

function daysAgo(days: number): string {
  const d = new Date(NOW);
  d.setDate(d.getDate() - days);
  return d.toISOString();
}

export const cases: Case[] = [
  {
    id: 'CASE-0001',
    customerId: 'CUST-1024',
    customer: 'CUST-1024',
    risk: 'high',
    status: 'investigating',
    assignedTo: 'Analyst A. Kumar',
    fraudType: 'Rapid Transaction Velocity',
    createdAt: daysAgo(2),
    updatedAt: daysAgo(0),
    summary: 'Multiple high-value online transactions within a short window. Customer has no history of this spending pattern.',
    findings: 'Four transactions totaling $19,400 posted within 45 minutes. All were online. Device profile matches customer\'s known device.',
    evidence: [
      {
        id: 'EVD-0001',
        caseId: 'CASE-0001',
        source: 'Transaction Log',
        type: 'transaction',
        timestamp: daysAgo(0),
        confidence: 'high',
        strength: 'strong',
        description: 'Online purchase of $4,850.00 flagged by risk model',
        relatedEntities: ['TXN-4850', 'CUST-1024'],
      },
      {
        id: 'EVD-0002',
        caseId: 'CASE-0001',
        source: 'Device Profile',
        type: 'device',
        timestamp: daysAgo(0),
        confidence: 'medium',
        strength: 'moderate',
        description: 'Transaction originated from known customer device',
        relatedEntities: ['DEV-9F3A', 'CUST-1024'],
      },
    ],
    actions: [
      {
        id: 'ACT-0001',
        caseId: 'CASE-0001',
        type: 'approve',
        target: 'STEP_UP_AUTH',
        note: 'Requested step-up authentication',
        timestamp: daysAgo(0),
        performedBy: 'System Agent',
      },
    ],
    decisions: [
      {
        id: 'DEC-0001',
        caseId: 'CASE-0001',
        action: 'Step-up authentication required',
        reason: 'Velocity pattern detected but device is known',
        timestamp: daysAgo(0),
        approvedBy: 'System Agent',
      },
    ],
    timeline: [
      { id: 'TLE-0001', timestamp: daysAgo(2), event: 'Case created from risk alert', type: 'created' },
      { id: 'TLE-0002', timestamp: daysAgo(0), event: 'Step-up authentication requested', type: 'action' },
    ],
    similarCases: [
      { id: 'CASE-0003', similarity: 0.78, matchingEntities: ['CUST-1024', 'DEV-9F3A'], matchingPatterns: ['Rapid transaction velocity'], outcome: 'Confirmed fraud' },
    ],
  },
  {
    id: 'CASE-0002',
    customerId: 'CUST-0845',
    customer: 'CUST-0845',
    risk: 'medium',
    status: 'new',
    assignedTo: 'Unassigned',
    fraudType: 'Device Anomaly',
    createdAt: daysAgo(1),
    updatedAt: daysAgo(1),
    summary: 'New device detected on account during online transaction.',
    findings: 'Transaction originated from a device not previously associated with this customer.',
    evidence: [
      {
        id: 'EVD-0003',
        caseId: 'CASE-0002',
        source: 'Device Profile',
        type: 'device',
        timestamp: daysAgo(1),
        confidence: 'high',
        strength: 'strong',
        description: 'New device detected — no prior association with customer',
        relatedEntities: ['DEV-NEW-7742', 'CUST-0845'],
      },
    ],
    actions: [],
    decisions: [],
    timeline: [
      { id: 'TLE-0003', timestamp: daysAgo(1), event: 'Case created from device alert', type: 'created' },
    ],
    similarCases: [],
  },
  {
    id: 'CASE-0003',
    customerId: 'CUST-1567',
    customer: 'CUST-1567',
    risk: 'low',
    status: 'resolved',
    assignedTo: 'Analyst B. Patel',
    fraudType: 'Geographic Inconsistency',
    createdAt: daysAgo(10),
    updatedAt: daysAgo(8),
    summary: 'Billing region mismatch detected. Verified as legitimate travel.',
    findings: 'Customer confirmed travel to the billing region. Case cleared.',
    evidence: [
      {
        id: 'EVD-0004',
        caseId: 'CASE-0003',
        source: 'Customer Confirmation',
        type: 'behavior',
        timestamp: daysAgo(8),
        confidence: 'high',
        strength: 'strong',
        description: 'Customer confirmed travel to billing region',
        relatedEntities: ['CUST-1567'],
      },
    ],
    actions: [
      {
        id: 'ACT-0002',
        caseId: 'CASE-0003',
        type: 'approve',
        target: 'CLOSE_NO_FRAUD',
        note: 'Case closed — no fraud detected',
        timestamp: daysAgo(8),
        performedBy: 'Analyst B. Patel',
      },
    ],
    decisions: [
      {
        id: 'DEC-0002',
        caseId: 'CASE-0003',
        action: 'Close case — no fraud',
        reason: 'Customer confirmed travel',
        timestamp: daysAgo(8),
        approvedBy: 'Analyst B. Patel',
      },
    ],
    timeline: [
      { id: 'TLE-0004', timestamp: daysAgo(10), event: 'Case created', type: 'created' },
      { id: 'TLE-0005', timestamp: daysAgo(8), event: 'Case closed — no fraud', type: 'decision' },
    ],
    similarCases: [],
  },
];

export function getCases(): Promise<Case[]> {
  return Promise.resolve(cases);
}

export function getCase(id: string): Promise<Case | undefined> {
  return Promise.resolve(cases.find((c) => c.id === id));
}