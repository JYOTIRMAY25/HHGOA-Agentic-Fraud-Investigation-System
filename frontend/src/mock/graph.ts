// HHGOA Mock Graph Data
// DEMO DATA — TigerGraph offline. Replace with real backend when available.

import type { GraphNode, GraphEdge } from '@/types';

export const graphNodes: GraphNode[] = [
  {
    id: 'CUST-1024',
    type: 'customer',
    label: 'CUST-1024',
    suspicious: false,
    data: { name: 'Customer 1024', accountAge: 3.2, transactionVolume: 48500 },
  },
  {
    id: 'CUST-2109',
    type: 'customer',
    label: 'CUST-2109',
    suspicious: true,
    data: { name: 'Customer 2109', accountAge: 0.4, transactionVolume: 12400 },
  },
  {
    id: 'ACC-1024',
    type: 'account',
    label: 'ACC-1024-A',
    suspicious: false,
    data: { type: 'checking', balance: 24500, openedAt: '2023-06-15' },
  },
  {
    id: 'ACC-2109',
    type: 'account',
    label: 'ACC-2109-A',
    suspicious: true,
    data: { type: 'checking', balance: 3200, openedAt: '2026-05-20' },
  },
  {
    id: 'TXN-4850',
    type: 'transaction',
    label: 'TXN-4850',
    suspicious: true,
    data: { amount: 4850.00, merchant: 'Online Electronics', channel: 'online', riskScore: 0.87 },
  },
  {
    id: 'TXN-4851',
    type: 'transaction',
    label: 'TXN-4851',
    suspicious: true,
    data: { amount: 4.50, merchant: 'Test Merchant', channel: 'online', riskScore: 0.45 },
  },
  {
    id: 'TXN-4852',
    type: 'transaction',
    label: 'TXN-4852',
    suspicious: true,
    data: { amount: 3.25, merchant: 'Test Merchant', channel: 'online', riskScore: 0.52 },
  },
  {
    id: 'DEV-9F3A',
    type: 'device',
    label: 'DEV-9F3A',
    suspicious: true,
    data: { type: 'mobile', os: 'Android 13', browser: 'Chrome 118', status: 'suspicious' },
  },
  {
    id: 'DEV-NEW-7742',
    type: 'device',
    label: 'DEV-NEW-7742',
    suspicious: true,
    data: { type: 'desktop', os: 'Windows 11', browser: 'Firefox 120', status: 'new' },
  },
  {
    id: 'MERC-ELEC',
    type: 'merchant',
    label: 'Online Electronics',
    suspicious: true,
    data: { category: 'Electronics', location: 'Online', riskLevel: 'high' },
  },
  {
    id: 'MERC-TEST',
    type: 'merchant',
    label: 'Test Merchant',
    suspicious: true,
    data: { category: 'Services', location: 'Online', riskLevel: 'medium' },
  },
  {
    id: 'IP-ANON-01',
    type: 'ip',
    label: 'IP-ANON-01',
    suspicious: true,
    data: { proxy: 'anonymous', country: 'Unknown' },
  },
];

export const graphEdges: GraphEdge[] = [
  { id: 'E1', source: 'CUST-1024', target: 'ACC-1024', label: 'OWNS', suspicious: false },
  { id: 'E2', source: 'ACC-1024', target: 'TXN-4850', label: 'MADE', suspicious: true },
  { id: 'E3', source: 'TXN-4850', target: 'DEV-9F3A', label: 'USED_DEVICE', suspicious: true },
  { id: 'E4', source: 'TXN-4850', target: 'MERC-ELEC', label: 'PURCHASED_FROM', suspicious: true },
  { id: 'E5', source: 'TXN-4850', target: 'IP-ANON-01', label: 'CONNECTED_TO', suspicious: true },
  { id: 'E6', source: 'CUST-1024', target: 'DEV-9F3A', label: 'USES', suspicious: true },
  { id: 'E7', source: 'DEV-9F3A', target: 'CUST-2109', label: 'LINKED_TO', suspicious: true },
  { id: 'E8', source: 'CUST-2109', target: 'ACC-2109', label: 'OWNS', suspicious: true },
  { id: 'E9', source: 'ACC-2109', target: 'TXN-4851', label: 'MADE', suspicious: true },
  { id: 'E10', source: 'TXN-4851', target: 'DEV-9F3A', label: 'USED_DEVICE', suspicious: true },
  { id: 'E11', source: 'TXN-4851', target: 'MERC-TEST', label: 'PURCHASED_FROM', suspicious: true },
  { id: 'E12', source: 'TXN-4850', target: 'TXN-4851', label: 'NEXT_TRANSACTION', suspicious: true },
  { id: 'E13', source: 'CUST-0845', target: 'DEV-NEW-7742', label: 'USES', suspicious: true },
  { id: 'E14', source: 'DEV-NEW-7742', target: 'CUST-2210', label: 'LINKED_TO', suspicious: true },
  { id: 'E15', source: 'DEV-NEW-7742', target: 'CUST-0744', label: 'LINKED_TO', suspicious: true },
];

export function getGraph(): Promise<{ nodes: GraphNode[]; edges: GraphEdge[] }> {
  return Promise.resolve({ nodes: graphNodes, edges: graphEdges });
}

export function getGraphForCase(caseId: string): Promise<{ nodes: GraphNode[]; edges: GraphEdge[] }> {
  return getGraph();
}