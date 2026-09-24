import React from 'react';
import { TrendingUp, AlertTriangle, Clock, CheckCircle } from 'lucide-react';
import type { DashboardKpis, RiskOverview } from '@/types';

interface KpiCardProps {
  title: string;
  value: number | string;
  change?: { value: number; label: string };
  icon: React.ReactNode;
  accent?: 'blue' | 'red' | 'amber' | 'emerald';
}

const accentStyles = {
  blue: 'bg-accent-blue/10 text-accent-blue',
  red: 'bg-risk-critical/10 text-risk-critical',
  amber: 'bg-risk-high/10 text-risk-high',
  emerald: 'bg-status-resolved/10 text-status-resolved',
};

export const KpiCard: React.FC<KpiCardProps> = ({ title, value, change, icon, accent = 'blue' }) => (
  <div className="card p-4 flex flex-col gap-3">
    <div className="flex items-center justify-between">
      <span className="text-xs font-medium text-text-secondary uppercase tracking-wide">{title}</span>
      <div className={`p-2 rounded-md ${accentStyles[accent]}`}>{icon}</div>
    </div>
    <div>
      <div className="text-2xl font-bold text-text-primary font-mono">{value}</div>
      {change && (
        <div className="flex items-center gap-1 mt-1">
          <TrendingUp className="w-3 h-3 text-status-resolved" />
          <span className="text-xs text-status-resolved">{change.value > 0 ? '+' : ''}{change.value}%</span>
          <span className="text-xs text-text-tertiary">{change.label}</span>
        </div>
      )}
    </div>
  </div>
);

interface RiskOverviewCardProps {
  data: RiskOverview;
}

export const RiskOverviewCard: React.FC<RiskOverviewCardProps> = ({ data }) => {
  const total = data.critical + data.high + data.medium + data.low;
  const items: { label: string; value: number; color: string; pct: number }[] = [
    { label: 'Critical', value: data.critical, color: 'bg-risk-critical', pct: total > 0 ? (data.critical / total) * 100 : 0 },
    { label: 'High', value: data.high, color: 'bg-risk-high', pct: total > 0 ? (data.high / total) * 100 : 0 },
    { label: 'Medium', value: data.medium, color: 'bg-risk-medium', pct: total > 0 ? (data.medium / total) * 100 : 0 },
    { label: 'Low', value: data.low, color: 'bg-status-resolved', pct: total > 0 ? (data.low / total) * 100 : 0 },
  ];

  return (
    <div className="card p-4">
      <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wide mb-3">Risk Overview</h3>
      <div className="space-y-2.5">
        {items.map((item) => (
          <div key={item.label} className="flex items-center gap-3">
            <span className="text-xs text-text-secondary w-16">{item.label}</span>
            <div className="flex-1 h-2 bg-bg-tertiary rounded-full overflow-hidden">
              <div
                className={`h-full ${item.color} transition-all duration-500`}
                style={{ width: `${item.pct}%` }}
              />
            </div>
            <span className="text-xs font-mono text-text-primary w-6 text-right">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

interface DistributionItem {
  label: string;
  value: number;
  color: string;
}

interface DistributionCardProps {
  title: string;
  items: DistributionItem[];
}

export const DistributionCard: React.FC<DistributionCardProps> = ({ title, items }) => {
  const total = items.reduce((s, i) => s + i.value, 0);
  return (
    <div className="card p-4">
      <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wide mb-3">{title}</h3>
      <div className="space-y-2">
        {items.map((item) => (
          <div key={item.label} className="flex items-center gap-3">
            <span className="text-xs text-text-secondary w-32 truncate">{item.label}</span>
            <div className="flex-1 h-2 bg-bg-tertiary rounded-full overflow-hidden">
              <div
                className={`h-full ${item.color} transition-all duration-500`}
                style={{ width: `${total > 0 ? (item.value / total) * 100 : 0}%` }}
              />
            </div>
            <span className="text-xs font-mono text-text-primary w-6 text-right">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};