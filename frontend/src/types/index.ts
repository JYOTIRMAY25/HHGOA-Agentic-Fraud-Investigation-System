export type RiskLevel = 'critical' | 'high' | 'medium' | 'low';
export type CaseStatus = 'new' | 'investigating' | 'awaiting_evidence' | 'escalated' | 'resolved' | 'closed';
export type InvestigationStatus = 'pending' | 'in_progress' | 'awaiting_evidence' | 'escalated' | 'completed' | 'closed';
export type ActionStatus = 'pending' | 'approved' | 'rejected' | 'escalated' | 'executed';
export type EvidenceType = 'transaction' | 'identity' | 'device' | 'behavior' | 'historical' | 'graph';
export type ConfidenceLevel = 'high' | 'medium' | 'low';
export type ChannelType = 'online' | 'in_person';
export type EvidenceStrength = 'strong' | 'moderate' | 'weak';
export type ApprovalRoute = 'auto' | 'L1' | 'L2';
export type AgentStatus = 'idle' | 'investigating' | 'awaiting_evidence' | 'ready' | 'escalated';

export interface Customer {
  id: string;
  name: string;
  accountNumber: string;
  deviceId: string;
  location: string;
  accountAge: number;
  transactionVolume: number;
  recentActivity: string;
}

export interface Account {
  id: string;
  customerId: string;
  type: 'checking' | 'savings' | 'credit';
  balance: number;
  openedAt: string;
}

export interface Transaction {
  id: string;
  timestamp: string;
  amount: number;
  merchant: string;
  deviceId: string;
  location: string;
  riskSignal: string;
  riskLevel: RiskLevel;
  channel: ChannelType;
  flagged: boolean;
}

export interface Device {
  id: string;
  type: string;
  os: string;
  browser: string;
  status: 'new' | 'known' | 'suspicious';
  linkedAccounts: string[];
}

export interface Merchant {
  id: string;
  name: string;
  category: string;
  location: string;
  riskLevel: RiskLevel;
}

export interface Evidence {
  id: string;
  caseId: string;
  source: string;
  type: EvidenceType;
  timestamp: string;
  confidence: ConfidenceLevel;
  strength: EvidenceStrength;
  description: string;
  relatedEntities: string[];
  expanded?: boolean;
}

export interface FraudPattern {
  id: string;
  name: string;
  severity: RiskLevel;
  confidence: ConfidenceLevel;
  supportingEvidenceCount: number;
  description: string;
  relatedEntities: string[];
  detectionSource: string;
}

export interface Recommendation {
  id: string;
  caseId: string;
  title: string;
  description: string;
  reason: string;
  evidenceCount: number;
  confidence: ConfidenceLevel;
  approvalRoute: ApprovalRoute;
  status: ActionStatus;
  createdAt: string;
}

export interface Action {
  id: string;
  caseId: string;
  type: 'approve' | 'reject' | 'escalate' | 'request_evidence';
  target?: string;
  note?: string;
  timestamp: string;
  performedBy: string;
}

export interface Decision {
  id: string;
  caseId: string;
  action: string;
  reason: string;
  timestamp: string;
  approvedBy?: string;
}

export interface Investigation {
  id: string;
  caseId: string;
  trigger: string;
  customer: string;
  riskScore: number;
  fraudPattern: string;
  evidenceCount: number;
  status: InvestigationStatus;
  createdAt: string;
  updatedAt: string;
  type: 'transaction_spike' | 'device_anomaly' | 'geographic' | 'account_takeover' | 'identity_mismatch';
}

export interface Case {
  id: string;
  customerId: string;
  customer: string;
  risk: RiskLevel;
  status: CaseStatus;
  assignedTo: string;
  fraudType: string;
  createdAt: string;
  updatedAt: string;
  summary?: string;
  findings?: string;
  evidence?: Evidence[];
  actions?: Action[];
  decisions?: Decision[];
  timeline?: TimelineEvent[];
  similarCases?: SimilarCase[];
}

export interface TimelineEvent {
  id: string;
  timestamp: string;
  event: string;
  type: 'created' | 'updated' | 'action' | 'decision' | 'evidence';
}

export interface SimilarCase {
  id: string;
  similarity: number;
  matchingEntities: string[];
  matchingPatterns: string[];
  outcome: string;
}

export interface GraphNode {
  id: string;
  type: 'customer' | 'account' | 'device' | 'transaction' | 'merchant' | 'ip' | 'address';
  label: string;
  suspicious: boolean;
  data: Record<string, any>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  suspicious: boolean;
}

export interface CaseMemory {
  similarCases: SimilarCase[];
  previousDecisions: Decision[];
  previousActions: Action[];
  recurringEntities: string[];
  recurringDevices: string[];
  recurringMerchants: string[];
  historicalOutcomes: string[];
}

export interface DashboardKpis {
  activeInvestigations: number;
  highRiskCases: number;
  pendingActions: number;
  investigationsToday: number;
}

export interface RiskOverview {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export interface ActivityDataPoint {
  date: string;
  investigations: number;
  alerts: number;
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'alert' | 'info' | 'warning' | 'success';
  timestamp: string;
  read: boolean;
}

export interface SystemStatus {
  status: 'operational' | 'degraded' | 'offline';
  tigergraph: 'connected' | 'disconnected' | 'connecting';
  agent: 'online' | 'offline';
  lastSync: string;
}

export interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
}

export interface AgentAssessment {
  investigationId: string;
  status: AgentStatus;
  assessment: string;
  riskAssessment: string;
  confidence: ConfidenceLevel;
  uncertainty: string;
  evidenceFound: string[];
  missingEvidence: string[];
  nextBestAction: string;
  policyRequirement: string;
  approvalRoute: ApprovalRoute;
  evidenceCount: number;
  patternsDetected: FraudPattern[];
  actionHistory: Action[];
  isDemo: true;
}

export interface EvidenceRequest {
  id: string;
  investigationId: string;
  type: 'customer_validation' | 'step_up_auth' | 'analyst_info';
  requestedAt: string;
  status: 'pending' | 'submitted';
  assumedResponse?: string;
}