import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Shield, ArrowLeft, Search, AlertTriangle, CheckCircle,
  Clock, Cpu, Database, MapPin, Mail, CreditCard, User,
  Activity, ChevronRight, Loader2,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
interface InvestigationResult {
  transaction_id: string;
  engine: string;
  investigation: { verdict: string; fraud_probability: number; summary: string };
  evidence: Array<{ source_tool: string; type: string; entity: string; relationship: string; attributes: Record<string, unknown> }>;
  risk_signals: Array<{ signal: string; severity: string; guidance: string; policy_rule?: string }>;
  related_entities: string[];
  historical_precedents: string[];
  uncertainty: string[];
  next_best_actions: Array<{ action: string; route: string; reason: string }>;
  next_best_action: string;
  approval_route: string;
  reasoning: string;
  tool_calls: Array<{ tool: string; status: string; summary: string }>;
  warnings: string[];
}

// ---------------------------------------------------------------------------
// Investigation steps shown during loading
// ---------------------------------------------------------------------------
const STEPS = [
  'Connecting to TigerGraph',
  'Gathering transaction evidence',
  'Tracing connected entities',
  'Checking fraud patterns',
  'Retrieving historical cases',
  'Applying policy rules',
  'Generating next-best action',
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function severityColor(s: string) {
  const m: Record<string, string> = {
    CRITICAL: 'text-risk-critical border-risk-critical/40 bg-risk-critical/10',
    HIGH: 'text-risk-high border-risk-high/40 bg-risk-high/10',
    MEDIUM: 'text-risk-medium border-risk-medium/40 bg-risk-medium/10',
    LOW: 'text-risk-low border-risk-low/40 bg-risk-low/10',
  };
  return m[s?.toUpperCase()] ?? 'text-text-secondary border-border-default bg-bg-tertiary';
}

function verdictColor(v: string) {
  if (v === 'fraud') return 'text-risk-critical';
  if (v === 'legitimate') return 'text-risk-low';
  return 'text-risk-medium';
}

function routeColor(r: string) {
  if (r === 'L2') return 'bg-risk-critical/15 text-risk-critical border-risk-critical/30';
  if (r === 'L1') return 'bg-risk-high/15 text-risk-high border-risk-high/30';
  return 'bg-accent-blue/15 text-accent-blue border-accent-blue/30';
}

function evidenceIcon(type: string) {
  if (type.includes('CARD')) return <CreditCard className="w-3.5 h-3.5" />;
  if (type.includes('DEVICE')) return <Cpu className="w-3.5 h-3.5" />;
  if (type.includes('REGION') || type.includes('GEO')) return <MapPin className="w-3.5 h-3.5" />;
  if (type.includes('EMAIL')) return <Mail className="w-3.5 h-3.5" />;
  if (type.includes('TRANSACTION')) return <Activity className="w-3.5 h-3.5" />;
  if (type.includes('CASE') || type.includes('HISTORICAL')) return <Database className="w-3.5 h-3.5" />;
  return <ChevronRight className="w-3.5 h-3.5" />;
}

// ---------------------------------------------------------------------------
// Loading overlay
// ---------------------------------------------------------------------------
function LoadingOverlay({ step }: { step: number }) {
  return (
    <div className="flex flex-col items-center justify-center py-24 gap-6">
      <div className="relative w-16 h-16">
        <div className="absolute inset-0 rounded-full border-2 border-accent-blue/20" />
        <div className="absolute inset-0 rounded-full border-2 border-t-accent-blue animate-spin" />
        <Shield className="absolute inset-0 m-auto w-6 h-6 text-accent-blue" />
      </div>
      <div className="text-center">
        <p className="text-sm font-medium text-text-primary mb-1">Agent investigating graph…</p>
        <p className="text-xs text-accent-blue font-mono">{STEPS[Math.min(step, STEPS.length - 1)]}</p>
      </div>
      <div className="w-64 space-y-1.5">
        {STEPS.map((s, i) => (
          <div key={s} className="flex items-center gap-2">
            <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${i < step ? 'bg-accent-blue' : i === step ? 'bg-accent-blue animate-pulse' : 'bg-border-default'}`} />
            <span className={`text-xs ${i <= step ? 'text-text-secondary' : 'text-text-muted'}`}>{s}</span>
            {i < step && <CheckCircle className="w-3 h-3 text-accent-blue ml-auto" />}
            {i === step && <Loader2 className="w-3 h-3 text-accent-blue ml-auto animate-spin" />}
          </div>
        ))}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Result dashboard
// ---------------------------------------------------------------------------
function ResultDashboard({ data }: { data: InvestigationResult }) {
  const { investigation, evidence, risk_signals, related_entities, historical_precedents, uncertainty, next_best_actions, approval_route, reasoning, tool_calls } = data;

  const txnEv = evidence.find(e => e.type === 'TRANSACTION_RECORD');
  const cardEv = evidence.find(e => e.type === 'CARD_INSTRUMENT');
  const deviceEv = evidence.find(e => e.type === 'DEVICE_PROFILE');
  const geoEv = evidence.find(e => e.type === 'GEOGRAPHIC_DISPERSION');
  const testEv = evidence.find(e => e.type === 'CARD_TESTING_EVALUATION');
  const expEv = evidence.find(e => e.type === 'EXPOSURE_AGGREGATION');

  const txnAttr = (txnEv?.attributes ?? {}) as Record<string, unknown>;
  const cardAttr = (cardEv?.attributes ?? {}) as Record<string, unknown>;
  const deviceAttr = (deviceEv?.attributes ?? {}) as Record<string, unknown>;
  const geoAttr = (geoEv?.attributes ?? {}) as Record<string, unknown>;
  const expAttr = (expEv?.attributes ?? {}) as Record<string, unknown>;

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="flex items-center justify-between p-4 rounded-lg border border-border-default bg-bg-secondary">
        <div>
          <p className="text-xs text-text-tertiary uppercase tracking-widest mb-1">Investigation</p>
          <p className="text-xl font-black font-mono">/ {data.transaction_id}</p>
        </div>
        <div className="flex items-center gap-3">
          <span className={`text-2xl font-black uppercase ${verdictColor(investigation.verdict)}`}>
            {investigation.verdict}
          </span>
          <span className={`text-sm font-mono px-2 py-1 rounded border ${routeColor(approval_route)}`}>
            {approval_route}
          </span>
        </div>
      </div>

      {/* Summary */}
      <p className="text-sm text-text-secondary leading-relaxed px-1">{investigation.summary}</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Transaction */}
        <div className="rounded-lg border border-border-default bg-bg-secondary p-5">
          <h3 className="text-xs font-bold uppercase tracking-widest text-text-tertiary mb-4">Transaction</h3>
          <div className="space-y-2">
            {[
              ['Amount', txnAttr.amount != null ? `$${txnAttr.amount}` : '—'],
              ['Timestamp', String(txnAttr.ts ?? '—')],
              ['Channel', String(txnAttr.channel ?? '—')],
              ['Product', String(txnAttr.product_cd ?? '—')],
              ['Risk Score', txnAttr.risk_score != null ? String(txnAttr.risk_score) : '—'],
              ['Card', cardEv ? String(cardEv.entity) : '—'],
              ['Network', String(cardAttr.network ?? '—')],
              ['Customer', String(cardAttr.customer_id ?? '—')],
            ].map(([k, v]) => (
              <div key={k} className="flex justify-between text-sm">
                <span className="text-text-tertiary">{k}</span>
                <span className="text-text-primary font-mono">{v}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Entity graph */}
        <div className="rounded-lg border border-border-default bg-bg-secondary p-5">
          <h3 className="text-xs font-bold uppercase tracking-widest text-text-tertiary mb-4">Entity Graph</h3>
          <div className="space-y-2">
            {related_entities.length > 0
              ? related_entities.map((e, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm text-text-secondary">
                    <ChevronRight className="w-3 h-3 text-accent-blue flex-shrink-0" />
                    <span>{e}</span>
                  </div>
                ))
              : <p className="text-sm text-text-tertiary">No connected entities found.</p>}
            {deviceEv && (
              <div className="mt-3 pt-3 border-t border-border-default space-y-1">
                {[
                  ['Device', String(deviceAttr.device_info ?? deviceEv.entity)],
                  ['OS', String(deviceAttr.os ?? '—')],
                  ['Status', String(deviceAttr.device_status ?? '—')],
                  ['Proxy', String(deviceAttr.proxy_flag ?? '—')],
                ].map(([k, v]) => (
                  <div key={k} className="flex justify-between text-xs">
                    <span className="text-text-tertiary">{k}</span>
                    <span className="text-text-secondary font-mono">{v}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Risk signals */}
      <div className="rounded-lg border border-border-default bg-bg-secondary p-5">
        <h3 className="text-xs font-bold uppercase tracking-widest text-text-tertiary mb-4">Risk Signals</h3>
        {risk_signals.length > 0 ? (
          <div className="space-y-3">
            {risk_signals.map((s, i) => (
              <div key={i} className={`flex items-start gap-3 p-3 rounded border ${severityColor(s.severity)}`}>
                <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-bold uppercase tracking-wide">{s.signal.replace(/_/g, ' ')}</span>
                    <span className="text-[10px] font-mono opacity-70">{s.severity}</span>
                    {s.policy_rule && <span className="text-[10px] font-mono opacity-70">[{s.policy_rule}]</span>}
                  </div>
                  <p className="text-xs opacity-80">{s.guidance}</p>
                </div>
              </div>
            ))}
            <p className="text-xs text-text-tertiary italic">Signals are evidence only — no fraud declared from a score alone.</p>
          </div>
        ) : (
          <p className="text-sm text-text-tertiary">No risk signals raised.</p>
        )}
      </div>

      {/* Evidence list */}
      <div className="rounded-lg border border-border-default bg-bg-secondary p-5">
        <h3 className="text-xs font-bold uppercase tracking-widest text-text-tertiary mb-4">Evidence ({evidence.length})</h3>
        <div className="space-y-1.5">
          {evidence.map((ev, i) => (
            <div key={i} className="flex items-start gap-2 text-xs text-text-secondary py-1 border-b border-border-default last:border-0">
              <span className="text-text-tertiary flex-shrink-0 mt-0.5">{evidenceIcon(ev.type)}</span>
              <span className="font-mono text-accent-blue/70 flex-shrink-0">[{ev.source_tool}]</span>
              <span className="flex-1">{ev.type} · {ev.entity}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Historical precedent */}
        <div className="rounded-lg border border-border-default bg-bg-secondary p-5">
          <h3 className="text-xs font-bold uppercase tracking-widest text-text-tertiary mb-4">Historical Precedent</h3>
          {historical_precedents.length > 0 ? (
            <div className="space-y-2">
              {historical_precedents.map((p, i) => (
                <div key={i} className="text-xs text-text-secondary p-2 rounded bg-bg-tertiary border border-border-default font-mono">{p}</div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-text-tertiary">No similar closed cases retrieved.</p>
          )}
        </div>

        {/* Case impact */}
        <div className="rounded-lg border border-border-default bg-bg-secondary p-5">
          <h3 className="text-xs font-bold uppercase tracking-widest text-text-tertiary mb-4">Case Impact</h3>
          <div className="space-y-3">
            {[
              ['Fraud Probability', `${(investigation.fraud_probability * 100).toFixed(0)}%`],
              ['Exposure', expAttr.total_exposure_usd != null ? `$${expAttr.total_exposure_usd}` : '—'],
              ['Fraud Txns', expAttr.fraud_transaction_count != null ? String(expAttr.fraud_transaction_count) : '—'],
              ['Approval Route', approval_route],
              ['Regions', geoAttr.distinct_regions != null ? String(geoAttr.distinct_regions) : '—'],
              ['International', geoAttr.foreign_transaction_count != null ? String(geoAttr.foreign_transaction_count) : '—'],
            ].map(([k, v]) => (
              <div key={k} className="flex justify-between text-sm">
                <span className="text-text-tertiary">{k}</span>
                <span className="text-text-primary font-mono">{v}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Next best action — hero panel */}
      <div className={`rounded-lg border-2 p-6 ${approval_route === 'L2' ? 'border-risk-critical/50 bg-risk-critical/5' : approval_route === 'L1' ? 'border-risk-high/50 bg-risk-high/5' : 'border-accent-blue/50 bg-accent-blue/5'}`}>
        <h3 className="text-xs font-bold uppercase tracking-widest text-text-tertiary mb-4">Next Best Action</h3>
        <div className="space-y-3">
          {next_best_actions.map((a, i) => (
            <div key={i} className="flex items-start gap-3">
              <span className={`text-[10px] font-bold px-2 py-1 rounded border flex-shrink-0 ${routeColor(a.route)}`}>{a.route}</span>
              <div>
                <p className="text-sm font-bold text-text-primary">{a.action}</p>
                <p className="text-xs text-text-secondary mt-0.5">{a.reason}</p>
              </div>
            </div>
          ))}
        </div>
        {uncertainty.length > 0 && (
          <div className="mt-4 pt-4 border-t border-border-default">
            <p className="text-xs font-bold uppercase tracking-widest text-text-tertiary mb-2">Uncertainty</p>
            {uncertainty.map((u, i) => (
              <p key={i} className="text-xs text-text-secondary mb-1">· {u}</p>
            ))}
          </div>
        )}
      </div>

      {/* Reasoning */}
      <div className="rounded-lg border border-border-default bg-bg-secondary p-5">
        <h3 className="text-xs font-bold uppercase tracking-widest text-text-tertiary mb-3">Reasoning</h3>
        <p className="text-sm text-text-secondary leading-relaxed">{reasoning}</p>
      </div>

      {/* MCP tool calls */}
      <div className="rounded-lg border border-border-default bg-bg-secondary p-5">
        <h3 className="text-xs font-bold uppercase tracking-widest text-text-tertiary mb-3">MCP Tools Called ({tool_calls.length})</h3>
        <div className="space-y-1">
          {tool_calls.map((t, i) => (
            <div key={i} className="flex items-center gap-2 text-xs font-mono">
              <span className={t.status === 'ok' ? 'text-risk-low' : 'text-risk-critical'}>●</span>
              <span className="text-accent-blue">{t.tool}</span>
              <span className="text-text-tertiary truncate">{t.summary}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------
export default function InvestigationPage() {
  const navigate = useNavigate();
  const [txnId, setTxnId] = useState('3514030');
  const [loading, setLoading] = useState(false);
  const [loadStep, setLoadStep] = useState(0);
  const [result, setResult] = useState<InvestigationResult | null>(null);
  const [error, setError] = useState('');

  async function runInvestigation() {
    if (!txnId.trim()) return;
    setLoading(true);
    setResult(null);
    setError('');
    setLoadStep(0);

    // Advance the step indicator while the real API call runs
    const interval = setInterval(() => {
      setLoadStep(s => Math.min(s + 1, STEPS.length - 2));
    }, 600);

    try {
      const res = await fetch('/investigate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transaction_id: txnId.trim() }),
      });
      clearInterval(interval);
      setLoadStep(STEPS.length - 1);
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail ?? `HTTP ${res.status}`);
      }
      const data: InvestigationResult = await res.json();
      setResult(data);
    } catch (e: unknown) {
      clearInterval(interval);
      setError(e instanceof Error ? e.message : 'Investigation failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-bg-primary text-text-primary">
      {/* Top bar */}
      <header className="sticky top-0 z-20 flex items-center gap-4 px-6 py-4 bg-bg-secondary/95 backdrop-blur border-b border-border-default">
        <button onClick={() => navigate('/')} className="p-1.5 rounded-md text-text-tertiary hover:text-text-primary hover:bg-bg-tertiary transition-colors">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-accent-blue" />
          <span className="text-sm font-bold uppercase tracking-tight">HHGOA</span>
          <span className="text-text-tertiary">/</span>
          <span className="text-sm text-text-secondary">Investigation</span>
        </div>
        <div className="ml-auto flex items-center gap-2 text-xs text-text-tertiary">
          <div className="w-1.5 h-1.5 rounded-full bg-risk-low animate-pulse" />
          Mock Mode
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-10">
        {/* Input */}
        <div className="mb-10">
          <h1 className="text-3xl font-black uppercase tracking-tight mb-2">Fraud Investigation</h1>
          <p className="text-sm text-text-secondary mb-6">Enter a transaction ID to begin an autonomous graph investigation.</p>
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-tertiary" />
              <input
                type="text"
                value={txnId}
                onChange={e => setTxnId(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && runInvestigation()}
                placeholder="Enter Transaction ID"
                className="w-full pl-9 pr-4 py-3 bg-bg-secondary border border-border-default rounded-md text-text-primary placeholder-text-tertiary focus:outline-none focus:border-accent-blue focus:ring-1 focus:ring-accent-blue font-mono"
              />
            </div>
            <button
              onClick={runInvestigation}
              disabled={loading || !txnId.trim()}
              className="px-6 py-3 bg-accent-blue hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold text-sm uppercase tracking-widest rounded-md transition-colors flex items-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
              Investigate
            </button>
          </div>
          <p className="text-xs text-text-tertiary mt-2">Demo: try <button onClick={() => setTxnId('3514030')} className="text-accent-blue hover:underline">3514030</button></p>
        </div>

        {/* States */}
        {loading && <LoadingOverlay step={loadStep} />}

        {error && !loading && (
          <div className="flex items-center gap-3 p-4 rounded-lg border border-risk-critical/40 bg-risk-critical/10 text-risk-critical">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            <div>
              <p className="text-sm font-bold">Investigation failed</p>
              <p className="text-xs mt-0.5 opacity-80">{error}</p>
            </div>
          </div>
        )}

        {result && !loading && <ResultDashboard data={result} />}
      </main>
    </div>
  );
}
