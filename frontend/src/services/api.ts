// HHGOA API Service Layer
// DEMO MODE — all data comes from local mock modules.
// When the real backend is available, replace the mock imports
// with HTTP calls to the MCP/TigerGraph backend.

import { isDemoMode } from '@/config';
import { apiPath } from '@/services/api-client';
import * as mockInvestigations from '@/mock/investigations';
import * as mockCases from '@/mock/cases';
import * as mockEvidence from '@/mock/evidence';
import * as mockGraph from '@/mock/graph';
import * as mockMemory from '@/mock/memory';
import * as mockAgent from '@/mock/agent';
import type {
  Investigation,
  Case,
  Evidence,
  GraphNode,
  GraphEdge,
  CaseMemory,
  AgentAssessment,
  Action,
  EvidenceRequest,
  DashboardKpis,
  RiskOverview,
  ActivityDataPoint,
  SimilarCase,
  FraudPattern,
} from '@/types';

// ---------------------------------------------------------------------------
// Investigations
// ---------------------------------------------------------------------------

export async function getInvestigations(): Promise<Investigation[]> {
  if (isDemoMode()) return mockInvestigations.getInvestigations();
  const res = await fetch(apiPath('/investigations'));
  return res.json();
}

export async function getInvestigation(id: string): Promise<Investigation | undefined> {
  if (isDemoMode()) return mockInvestigations.getInvestigation(id);
  const res = await fetch(apiPath(`/api/v1/investigations/${id}`));
  return res.json();
}

// ---------------------------------------------------------------------------
// Cases
// ---------------------------------------------------------------------------

export async function getCases(): Promise<Case[]> {
  if (isDemoMode()) return mockCases.getCases();
  const res = await fetch(apiPath('/api/v1/cases'));
  return res.json();
}

export async function getCase(id: string): Promise<Case | undefined> {
  if (isDemoMode()) return mockCases.getCase(id);
  const res = await fetch(apiPath(`/api/v1/cases/${id}`));
  return res.json();
}

// ---------------------------------------------------------------------------
// Evidence
// ---------------------------------------------------------------------------

export async function getEvidence(): Promise<Evidence[]> {
  if (isDemoMode()) return mockEvidence.getEvidence();
  const res = await fetch(apiPath('/api/v1/evidence'));
  return res.json();
}

export async function getEvidenceByCase(caseId: string): Promise<Evidence[]> {
  if (isDemoMode()) return mockEvidence.getEvidenceByCase(caseId);
  const res = await fetch(apiPath(`/api/v1/evidence?caseId=${caseId}`));
  return res.json();
}

// ---------------------------------------------------------------------------
// Graph
// ---------------------------------------------------------------------------

export async function getGraph(): Promise<{ nodes: GraphNode[]; edges: GraphEdge[] }> {
  if (isDemoMode()) return mockGraph.getGraph();
  const res = await fetch(apiPath('/api/v1/graph'));
  return res.json();
}

export async function getGraphForCase(caseId: string): Promise<{ nodes: GraphNode[]; edges: GraphEdge[] }> {
  if (isDemoMode()) return mockGraph.getGraphForCase(caseId);
  const res = await fetch(apiPath(`/api/v1/graph?caseId=${caseId}`));
  return res.json();
}

// ---------------------------------------------------------------------------
// Case Memory
// ---------------------------------------------------------------------------

export async function getCaseMemory(caseId?: string): Promise<CaseMemory> {
  if (isDemoMode()) return mockMemory.getCaseMemory(caseId);
  const url = caseId ? apiPath(`/api/v1/memory?caseId=${caseId}`) : apiPath('/api/v1/memory');
  const res = await fetch(url);
  return res.json();
}

export async function getSimilarCases(caseId: string): Promise<SimilarCase[]> {
  if (isDemoMode()) return mockMemory.getSimilarCases(caseId);
  const res = await fetch(apiPath(`/api/v1/memory/${caseId}/similar`));
  return res.json();
}

// ---------------------------------------------------------------------------
// Agent Assessment
// ---------------------------------------------------------------------------

export async function getAgentAssessment(investigationId: string): Promise<AgentAssessment> {
  if (isDemoMode()) return mockAgent.getAgentAssessment(investigationId);
  const res = await fetch(apiPath(`/api/v1/investigations/${investigationId}/agent`));
  return res.json();
}

export async function getFraudPatterns(investigationId: string): Promise<FraudPattern[]> {
  const assessment = await getAgentAssessment(investigationId);
  return assessment.patternsDetected;
}

// ---------------------------------------------------------------------------
// Actions
// ---------------------------------------------------------------------------

export async function requestEvidence(
  investigationId: string,
  type: 'customer_validation' | 'step_up_auth' | 'analyst_info'
): Promise<EvidenceRequest> {
  if (isDemoMode()) return mockAgent.requestEvidence(investigationId, type);
  const res = await fetch(apiPath(`/api/v1/investigations/${investigationId}/evidence-request`), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type }),
  });
  return res.json();
}

export async function approveAction(investigationId: string, actionId: string): Promise<Action> {
  if (isDemoMode()) return mockAgent.approveAction(investigationId, actionId);
  const res = await fetch(apiPath(`/api/v1/investigations/${investigationId}/actions/${actionId}/approve`), {
    method: 'POST',
  });
  return res.json();
}

export async function rejectAction(investigationId: string, actionId: string): Promise<Action> {
  if (isDemoMode()) return mockAgent.approveAction(investigationId, actionId);
  const res = await fetch(apiPath(`/api/v1/investigations/${investigationId}/actions/${actionId}/reject`), {
    method: 'POST',
  });
  return res.json();
}

export async function escalateInvestigation(investigationId: string): Promise<Action> {
  if (isDemoMode()) return mockAgent.escalateInvestigation(investigationId);
  const res = await fetch(`/api/v1/investigations/${investigationId}/escalate`, {
    method: 'POST',
  });
  return res.json();
}

// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------

export async function getDashboardKpis(): Promise<DashboardKpis> {
  const investigations = await getInvestigations();
  const cases = await getCases();

  return {
    activeInvestigations: investigations.filter((i) =>
      ['in_progress', 'awaiting_evidence'].includes(i.status)
    ).length,
    highRiskCases: cases.filter((c) => c.risk === 'high' || c.risk === 'critical').length,
    pendingActions: investigations.filter((i) => i.status === 'pending').length,
    investigationsToday: investigations.filter((i) => {
      const today = new Date().toDateString();
      return new Date(i.createdAt).toDateString() === today;
    }).length,
  };
}

export async function getRiskOverview(): Promise<RiskOverview> {
  const cases = await getCases();
  return {
    critical: cases.filter((c) => c.risk === 'critical').length,
    high: cases.filter((c) => c.risk === 'high').length,
    medium: cases.filter((c) => c.risk === 'medium').length,
    low: cases.filter((c) => c.risk === 'low').length,
  };
}

export async function getInvestigationActivity(): Promise<ActivityDataPoint[]> {
  return [
    { date: '2026-09-14', investigations: 3, alerts: 5 },
    { date: '2026-09-15', investigations: 2, alerts: 4 },
    { date: '2026-09-16', investigations: 5, alerts: 7 },
    { date: '2026-09-17', investigations: 4, alerts: 6 },
    { date: '2026-09-18', investigations: 6, alerts: 8 },
    { date: '2026-09-19', investigations: 3, alerts: 4 },
    { date: '2026-09-20', investigations: 2, alerts: 3 },
  ];
}