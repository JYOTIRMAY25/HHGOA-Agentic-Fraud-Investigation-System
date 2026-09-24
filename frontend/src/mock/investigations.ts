// HHGOA Mock Data Layer
// All data is DEMO/MOCK. TigerGraph is offline.
// These will be replaced by real backend calls when available.

import type { Investigation } from '@/types';

const NOW = '2026-09-20T11:00:00Z';

function daysAgo(days: number): string {
  const d = new Date(NOW);
  d.setDate(d.getDate() - days);
  return d.toISOString();
}

export const investigations: Investigation[] = [
  {
    id: 'INV-0001',
    caseId: 'CASE-0001',
    trigger: 'High-risk transaction alert — online purchase $4,850.00',
    customer: 'CUST-1024',
    riskScore: 87,
    fraudPattern: 'Rapid transaction velocity',
    evidenceCount: 12,
    status: 'in_progress',
    createdAt: daysAgo(2),
    updatedAt: daysAgo(0),
    type: 'transaction_spike',
  },
  {
    id: 'INV-0002',
    caseId: 'CASE-0002',
    trigger: 'New device detected on account',
    customer: 'CUST-0845',
    riskScore: 72,
    fraudPattern: 'Device reuse',
    evidenceCount: 8,
    status: 'in_progress',
    createdAt: daysAgo(1),
    updatedAt: daysAgo(1),
    type: 'device_anomaly',
  },
  {
    id: 'INV-0003',
    caseId: 'CASE-0003',
    trigger: 'Geographic inconsistency — billing region mismatch',
    customer: 'CUST-1567',
    riskScore: 64,
    fraudPattern: 'Geographic inconsistency',
    evidenceCount: 5,
    status: 'pending',
    createdAt: daysAgo(0),
    updatedAt: daysAgo(0),
    type: 'geographic',
  },
  {
    id: 'INV-0004',
    caseId: 'CASE-0004',
    trigger: 'Multiple failed login attempts',
    customer: 'CUST-2210',
    riskScore: 91,
    fraudPattern: 'Account takeover indicators',
    evidenceCount: 15,
    status: 'in_progress',
    createdAt: daysAgo(3),
    updatedAt: daysAgo(0),
    type: 'account_takeover',
  },
  {
    id: 'INV-0005',
    caseId: 'CASE-0005',
    trigger: 'Identity mismatch — email domain change',
    customer: 'CUST-0312',
    riskScore: 58,
    fraudPattern: 'Identity mismatch',
    evidenceCount: 6,
    status: 'awaiting_evidence',
    createdAt: daysAgo(4),
    updatedAt: daysAgo(2),
    type: 'identity_mismatch',
  },
  {
    id: 'INV-0006',
    caseId: 'CASE-0006',
    trigger: 'Unusual transaction behavior — off-hours activity',
    customer: 'CUST-1983',
    riskScore: 45,
    fraudPattern: 'Unusual transaction behavior',
    evidenceCount: 3,
    status: 'pending',
    createdAt: daysAgo(0),
    updatedAt: daysAgo(0),
    type: 'transaction_spike',
  },
  {
    id: 'INV-0007',
    caseId: 'CASE-0007',
    trigger: 'Linked suspicious entities detected',
    customer: 'CUST-0744',
    riskScore: 78,
    fraudPattern: 'Linked suspicious entities',
    evidenceCount: 11,
    status: 'in_progress',
    createdAt: daysAgo(5),
    updatedAt: daysAgo(1),
    type: 'device_anomaly',
  },
  {
    id: 'INV-0008',
    caseId: 'CASE-0008',
    trigger: 'Card testing pattern — micro-transactions',
    customer: 'CUST-1456',
    riskScore: 69,
    fraudPattern: 'Rapid transaction velocity',
    evidenceCount: 9,
    status: 'escalated',
    createdAt: daysAgo(6),
    updatedAt: daysAgo(1),
    type: 'transaction_spike',
  },
  {
    id: 'INV-0009',
    caseId: 'CASE-0009',
    trigger: 'Shared device across multiple accounts',
    customer: 'CUST-2109',
    riskScore: 82,
    fraudPattern: 'Device reuse',
    evidenceCount: 14,
    status: 'in_progress',
    createdAt: daysAgo(7),
    updatedAt: daysAgo(0),
    type: 'device_anomaly',
  },
  {
    id: 'INV-0010',
    caseId: 'CASE-0010',
    trigger: 'High-risk merchant category alert',
    customer: 'CUST-0533',
    riskScore: 51,
    fraudPattern: 'Unusual transaction behavior',
    evidenceCount: 4,
    status: 'completed',
    createdAt: daysAgo(10),
    updatedAt: daysAgo(8),
    type: 'transaction_spike',
  },
];

export function getInvestigations(): Promise<Investigation[]> {
  return Promise.resolve(investigations);
}

export function getInvestigation(id: string): Promise<Investigation | undefined> {
  return Promise.resolve(investigations.find((i) => i.id === id || i.caseId === id));
}

export function getInvestigationsByStatus(status: string): Promise<Investigation[]> {
  return Promise.resolve(investigations.filter((i) => i.status === status));
}