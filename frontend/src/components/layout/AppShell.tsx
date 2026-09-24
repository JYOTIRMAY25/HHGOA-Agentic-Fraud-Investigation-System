import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from '@/components/layout/Sidebar';
import { TopBar } from '@/components/layout/TopBar';

export const AppShell: React.FC = () => {
  return (
    <div className="min-h-screen bg-bg-primary text-text-primary">
      <Sidebar />
      <div className="lg:ml-64 transition-all duration-200">
        <TopBar />
        <main className="pt-14 min-h-screen">
          <div className="p-4 lg:p-6 max-w-[1600px] mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};