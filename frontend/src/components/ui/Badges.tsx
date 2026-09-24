import React from 'react';
import type { RiskLevel, CaseStatus, InvestigationStatus, ConfidenceLevel, EvidenceStrength } from '@/types';

const riskColors: Record<RiskLevel, string> = {
  critical: 'bg-risk-critical/15 text-risk-critical border-risk-critical/30',
  high: 'bg-risk-high/15 text-risk-high border-risk-high/30',
  medium: 'bg-risk-medium/15 text-risk-medium border-risk-medium/30',
  low: 'bg-risk-low/15 text-risk-low border-risk-low/30',
};

export const RiskBadge: React.FC<{ risk: RiskLevel; size?: 'sm' | 'md' }> = ({ risk, size = 'sm' }) => {
  const sizes = { sm: 'text-[10px] px-2 py-0.5', md: 'text-xs px-2.5 py-1' };
  return (
    <span className={`inline-flex items-center font-medium rounded border uppercase tracking-wide ${riskColors[risk]} ${sizes[size]}`}>
      {risk}
    </span>
  );
};

const statusColors: Record<CaseStatus, string> = {
  new: 'bg-status-new/15 text-status-new border-status-new/30',
  investigating: 'bg-status-investigating/15 text-status-investigating border-status-investigating/30',
  awaiting_evidence: 'bg-status-awaiting_evidence/15 text-status-awaiting_evidence border-status-awaiting_evidence/30',
  escalated: 'bg-status-escalated/15 text-status-escalated border-status-escalated/30',
  resolved: 'bg-status-resolved/15 text-status-resolved border-status-resolved/30',
  closed: 'bg-status-closed/15 text-status-closed border-status-closed/30',
};

const statusLabels: Record<CaseStatus, string> = {
  new: 'New',
  investigating: 'Investigating',
  awaiting_evidence: 'Awaiting Evidence',
  escalated: 'Escalated',
  resolved: 'Resolved',
  closed: 'Closed',
};

export const StatusBadge: React.FC<{ status: CaseStatus | InvestigationStatus; size?: 'sm' | 'md' }> = ({ status, size = 'sm' }) => {
  const sizes = { sm: 'text-[10px] px-2 py-0.5', md: 'text-xs px-2.5 py-1' };
  const color = statusColors[status as CaseStatus] || statusColors.new;
  const label = statusLabels[status as CaseStatus] || status;
  return (
    <span className={`inline-flex items-center font-medium rounded border whitespace-nowrap ${color} ${sizes[size]}`}>
      {label}
    </span>
  );
};

const confidenceColors: Record<ConfidenceLevel, string> = {
  high: 'text-risk-low',
  medium: 'text-risk-medium',
  low: 'text-text-tertiary',
};

export const ConfidenceBadge: React.FC<{ confidence: ConfidenceLevel }> = ({ confidence }) => (
  <span className={`text-xs font-medium capitalize ${confidenceColors[confidence]}`}>
    {confidence}
  </span>
);

const strengthColors: Record<EvidenceStrength, string> = {
  strong: 'text-risk-low',
  moderate: 'text-risk-medium',
  weak: 'text-text-tertiary',
};

export const StrengthBadge: React.FC<{ strength: EvidenceStrength }> = ({ strength }) => (
  <span className={`text-[10px] font-medium uppercase tracking-wide ${strengthColors[strength]}`}>
    {strength}
  </span>
);

export const RiskScore: React.FC<{ score: number; size?: 'sm' | 'md' | 'lg' }> = ({ score, size = 'md' }) => {
  const color = score >= 70 ? 'text-risk-critical' : score >= 40 ? 'text-risk-high' : 'text-risk-medium';
  const sizes = { sm: 'text-lg', md: 'text-2xl', lg: 'text-4xl' };
  return (
    <span className={`font-mono font-semibold ${color} ${sizes[size]}`}>
      {score}
    </span>
  );
};