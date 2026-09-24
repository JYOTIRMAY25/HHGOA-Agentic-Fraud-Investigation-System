import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Shield } from 'lucide-react';

export default function Architecture() {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-bg-primary text-text-primary">
      <header className="flex items-center gap-4 px-6 py-4 border-b border-border-default">
        <button onClick={() => navigate('/')} className="p-1.5 rounded-md text-text-tertiary hover:text-text-primary hover:bg-bg-tertiary transition-colors">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <Shield className="w-4 h-4 text-accent-blue" />
        <span className="text-sm font-bold uppercase">HHGOA / Architecture</span>
      </header>
      <main className="max-w-3xl mx-auto px-6 py-16">
        <h1 className="text-4xl font-black uppercase tracking-tight mb-8">Architecture</h1>
        <div className="space-y-4 font-mono text-sm text-text-secondary">
          {[
            'Frontend (React + Vite)  →  POST /investigate',
            '  ↓',
            'FastAPI (api/server.py)',
            '  ↓',
            'Gemini Agent (agent/investigator.py)',
            '  ↓  function-calling loop',
            'MCP Tool Executor',
            '  ↓  7 investigation tools',
            'TigerGraph (HHGOA_Fraud_Graph)',
            '  ↓  normalized evidence',
            'Policy Adjudicator (R1–R10)',
            '  ↓',
            'InvestigationReport → HTTP response',
          ].map((line, i) => (
            <div key={i} className={line.startsWith('  ') ? 'pl-4 text-text-tertiary' : 'text-text-primary font-bold'}>{line}</div>
          ))}
        </div>
        <div className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { label: 'MCP Tools', value: '7', desc: 'investigate_transaction, trace_connected_entities, detect_card_testing, analyze_region_anomalies, retrieve_similar_cases, calculate_case_exposure, validate_graph_metrics' },
            { label: 'Policy Rules', value: 'R1–R10', desc: 'Fraud policy v1.0 — verify before block, card testing, shared origin, escalation, SAR filing' },
            { label: 'Mock Mode', value: 'TG_MOCK_MODE', desc: 'Offline fixtures for demo without live TigerGraph. Set to false for live cluster.' },
          ].map(c => (
            <div key={c.label} className="p-4 rounded-lg border border-border-default bg-bg-secondary">
              <p className="text-xs text-text-tertiary uppercase tracking-widest mb-1">{c.label}</p>
              <p className="text-xl font-black text-accent-blue mb-2">{c.value}</p>
              <p className="text-xs text-text-secondary leading-relaxed">{c.desc}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
