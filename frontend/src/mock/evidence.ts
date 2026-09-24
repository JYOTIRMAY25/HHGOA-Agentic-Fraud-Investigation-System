// HHGOA Mock Evidence Data
// DEMO DATA — TigerGraph offline. Replace with real backend when available.

import type { Evidence } from '@/types';

const NOW = '2026-09-20T11:00:00Z';

function daysAgo(days: number): string {
  const d = new Date(NOW);
  d.setDate(d.getDate() - days);
  return d.toISOString();
}

export const evidence: Evidence[] = [
  {
    id: 'EVD-1001',
    caseId: 'CASE-0001',
    source: 'TigerGraph Query: investigate_transaction',
    type: 'transaction',
    timestamp: daysAgo(0),
    confidence: 'high',
    strength: 'strong',
    description: 'Online purchase of $4,850.00 — flagged by risk model at score 0.87',
    relatedEntities: ['TXN-4850', 'CUST-1024', 'DEV-9F3A'],
  },
  {
    id: 'EVD-1002',
    caseId: 'CASE-0001',
    source: 'TigerGraph Query: trace_connected_entities',
    type: 'graph',
    timestamp: daysAgo(0),
    confidence: 'high',
    strength: 'strong',
    description: 'Shared device relationship detected between CUST-1024 and CUST-2109',
    relatedEntities: ['DEV-9F3A', 'CUST-1024', 'CUST-2109'],
  },
  {
    id: 'EVD-1003',
    caseId: 'CASE-0001',
    source: 'TigerGraph Query: detect_card_testing',
    type: 'behavior',
    timestamp: daysAgo(0),
    confidence: 'medium',
    strength: 'moderate',
    description: 'Three micro-transactions under $5 followed by a larger purchase within 30 minutes',
    relatedEntities: ['TXN-4850', 'TXN-4851', 'TXN-4852', 'CUST-1024'],
  },
  {
    id: 'EVD-1004',
    caseId: 'CASE-0001',
    source: 'TigerGraph Query: retrieve_similar_cases',
    type: 'historical',
    timestamp: daysAgo(0),
    confidence: 'medium',
    strength: 'moderate',
    description: 'Historical case CASE-0003 shows similar pattern — confirmed fraud',
    relatedEntities: ['CASE-0003', 'CUST-1024'],
  },
  {
    id: 'EVD-1005',
    caseId: 'CASE-0001',
    source: 'Device Profile Service',
    type: 'device',
    timestamp: daysAgo(0),
    confidence: 'high',
    strength: 'strong',
    description: 'Device DEV-9F3A is marked as known for this customer',
    relatedEntities: ['DEV-9F3A', 'CUST-1024'],
  },
  {
    id: 'EVD-1006',
    caseId: 'CASE-0001',
    source: 'Identity Service',
    type: 'identity',
    timestamp: daysAgo(1),
    confidence: 'low',
    strength: 'weak',
    description: 'Email domain changed from customer\'s usual domain',
    relatedEntities: ['CUST-1024'],
  },
  {
    id: 'EVD-1007',
    caseId: 'CASE-0002',
    source: 'Device Profile Service',
    type: 'device',
    timestamp: daysAgo(1),
    confidence: 'high',
    strength: 'strong',
    description: 'New device detected — no prior association with customer',
    relatedEntities: ['DEV-NEW-7742', 'CUST-0845'],
  },
  {
    id: 'EVD-1008',
    caseId: 'CASE-0002',
    source: 'TigerGraph Query: trace_connected_entities',
    type: 'graph',
    timestamp: daysAgo(1),
    confidence: 'medium',
    strength: 'moderate',
    description: 'Device is also associated with two other accounts',
    relatedEntities: ['DEV-NEW-7742', 'CUST-0845', 'CUST-2210', 'CUST-0744'],
  },
];

export function getEvidence(): Promise<Evidence[]> {
  return Promise.resolve(evidence);
}

export function getEvidenceByCase(caseId: string): Promise<Evidence[]> {
  return Promise.resolve(evidence.filter((e) => e.caseId === caseId));
}

export function getEvidenceById(id: string): Promise<Evidence | undefined> {
  return Promise.resolve(evidence.find((e) => e.id === id));
}