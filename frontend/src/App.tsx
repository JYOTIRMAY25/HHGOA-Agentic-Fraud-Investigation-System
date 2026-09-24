import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ToastProvider } from '@/components/ui/Toast';
import { AppShell } from '@/components/layout/AppShell';

// Standalone pages (no sidebar)
import Landing from '@/pages/Landing';
import InvestigationPage from '@/pages/InvestigationPage';
import Architecture from '@/pages/Architecture';

// Sidebar pages (lazy)
const Dashboard = lazy(() => import('@/pages/Dashboard'));
const Investigations = lazy(() => import('@/pages/Investigations'));
const InvestigationWorkspace = lazy(() => import('@/pages/InvestigationWorkspace'));
const Cases = lazy(() => import('@/pages/Cases'));
const CaseDetail = lazy(() => import('@/pages/CaseDetail'));
const GraphExplorer = lazy(() => import('@/pages/GraphExplorer'));
const EvidenceExplorer = lazy(() => import('@/pages/EvidenceExplorer'));
const CaseMemory = lazy(() => import('@/pages/CaseMemory'));
const Settings = lazy(() => import('@/pages/Settings'));

const Spinner = () => (
  <div className="flex items-center justify-center h-64">
    <div className="w-8 h-8 rounded-full border-2 border-accent-blue border-t-transparent animate-spin" />
  </div>
);

export default function App() {
  return (
    <ToastProvider>
      <BrowserRouter>
        <Routes>
          {/* Standalone — no sidebar */}
          <Route path="/" element={<Landing />} />
          <Route path="/investigate" element={<InvestigationPage />} />
          <Route path="/architecture" element={<Architecture />} />

          {/* Sidebar shell */}
          <Route element={<AppShell />}>
            <Route path="/dashboard" element={<Suspense fallback={<Spinner />}><Dashboard /></Suspense>} />
            <Route path="/investigations" element={<Suspense fallback={<Spinner />}><Investigations /></Suspense>} />
            <Route path="/investigations/:id" element={<Suspense fallback={<Spinner />}><InvestigationWorkspace /></Suspense>} />
            <Route path="/cases" element={<Suspense fallback={<Spinner />}><Cases /></Suspense>} />
            <Route path="/cases/:id" element={<Suspense fallback={<Spinner />}><CaseDetail /></Suspense>} />
            <Route path="/graph" element={<Suspense fallback={<Spinner />}><GraphExplorer /></Suspense>} />
            <Route path="/evidence" element={<Suspense fallback={<Spinner />}><EvidenceExplorer /></Suspense>} />
            <Route path="/memory" element={<Suspense fallback={<Spinner />}><CaseMemory /></Suspense>} />
            <Route path="/settings" element={<Suspense fallback={<Spinner />}><Settings /></Suspense>} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ToastProvider>
  );
}
