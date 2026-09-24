import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, ArrowRight, Network, Search, Zap } from 'lucide-react';

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-bg-primary text-text-primary flex flex-col">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-5 border-b border-border-default">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-blue to-blue-700 flex items-center justify-center">
            <Shield className="w-4 h-4 text-white" />
          </div>
          <span className="text-sm font-bold tracking-tight uppercase">HHGOA</span>
          <span className="text-xs text-text-tertiary uppercase tracking-widest hidden sm:block">Fraud Intelligence</span>
        </div>
        <button
          onClick={() => navigate('/investigate')}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium bg-accent-blue hover:bg-blue-500 text-white rounded-md transition-colors"
        >
          Start Investigation <ArrowRight className="w-4 h-4" />
        </button>
      </nav>

      {/* Hero */}
      <section className="flex-1 flex flex-col items-center justify-center px-6 py-24 text-center max-w-4xl mx-auto w-full">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-accent-blue/30 bg-accent-blue/10 text-accent-blue text-xs font-medium uppercase tracking-widest mb-8">
          <div className="w-1.5 h-1.5 rounded-full bg-accent-blue animate-pulse" />
          Powered by Gemini · TigerGraph · MCP
        </div>

        <h1 className="text-5xl sm:text-6xl lg:text-7xl font-black tracking-tight leading-none mb-6 uppercase">
          Fraud doesn't hide<br />
          <span className="text-accent-blue">in data.</span><br />
          It hides in<br />
          <span className="text-accent-blue">relationships.</span>
        </h1>

        <p className="text-lg text-text-secondary max-w-xl mb-12">
          Agentic fraud investigation powered by Gemini, TigerGraph and MCP.
          Graph-native evidence. Policy-aware decisions.
        </p>

        <div className="flex flex-col sm:flex-row gap-4">
          <button
            onClick={() => navigate('/investigate')}
            className="flex items-center justify-center gap-2 px-8 py-4 bg-accent-blue hover:bg-blue-500 text-white font-bold text-sm uppercase tracking-widest rounded-md transition-colors"
          >
            Start Investigation <ArrowRight className="w-4 h-4" />
          </button>
          <button
            onClick={() => navigate('/architecture')}
            className="flex items-center justify-center gap-2 px-8 py-4 border border-border-hover hover:border-accent-blue text-text-secondary hover:text-text-primary font-bold text-sm uppercase tracking-widest rounded-md transition-colors"
          >
            View Architecture
          </button>
        </div>
      </section>

      {/* Three sections */}
      <section className="border-t border-border-default">
        <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-border-default max-w-6xl mx-auto">
          {[
            {
              num: '01',
              label: 'INVESTIGATE',
              icon: <Search className="w-5 h-5 text-accent-blue" />,
              desc: 'Transaction → Card → Customer → Device → Location',
            },
            {
              num: '02',
              label: 'CORRELATE',
              icon: <Network className="w-5 h-5 text-accent-cyan" />,
              desc: 'Graph relationships + historical cases + fraud patterns',
            },
            {
              num: '03',
              label: 'ACT',
              icon: <Zap className="w-5 h-5 text-accent-teal" />,
              desc: 'Policy-aware next-best action + approval route',
            },
          ].map((s) => (
            <div key={s.num} className="px-10 py-12">
              <div className="text-xs font-mono text-text-tertiary mb-4">{s.num} /</div>
              <div className="flex items-center gap-2 mb-3">
                {s.icon}
                <span className="text-sm font-bold uppercase tracking-widest">{s.label}</span>
              </div>
              <p className="text-sm text-text-secondary leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
