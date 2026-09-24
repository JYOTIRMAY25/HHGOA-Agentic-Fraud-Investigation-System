import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Search,
  FileSearch,
  FolderKanban,
  Network,
  Database,
  BookOpen,
  Settings,
  Activity,
  Shield,
  ChevronLeft,
  Menu,
  X,
} from 'lucide-react';
import { isDemoMode } from '@/config';

interface NavItem {
  label: string;
  to: string;
  icon: React.ReactNode;
  badge?: string;
}

const navItems: NavItem[] = [
  { label: 'Dashboard', to: '/', icon: <LayoutDashboard className="w-5 h-5" /> },
  { label: 'Investigations', to: '/investigations', icon: <FileSearch className="w-5 h-5" /> },
  { label: 'Cases', to: '/cases', icon: <FolderKanban className="w-5 h-5" /> },
  { label: 'Graph Explorer', to: '/graph', icon: <Network className="w-5 h-5" /> },
  { label: 'Evidence', to: '/evidence', icon: <Database className="w-5 h-5" /> },
  { label: 'Case Memory', to: '/memory', icon: <BookOpen className="w-5 h-5" /> },
  { label: 'Settings', to: '/settings', icon: <Settings className="w-5 h-5" /> },
];

export const Sidebar: React.FC = () => {
  const location = useLocation();
  const [collapsed, setCollapsed] = React.useState(false);
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const isActive = (to: string) => {
    if (to === '/') return location.pathname === '/';
    return location.pathname.startsWith(to);
  };

  const NavContent = () => (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 h-14 border-b border-border-default">
        <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-gradient-to-br from-accent-blue to-blue-700">
          <Shield className="w-5 h-5 text-white" />
        </div>
        {!collapsed && (
          <div className="flex flex-col">
            <span className="text-sm font-bold text-text-primary tracking-tight">HHGOA</span>
            <span className="text-[10px] text-text-tertiary uppercase tracking-widest">Fraud Intelligence</span>
          </div>
        )}
      </div>

      {/* Demo Indicator */}
      {isDemoMode() && (
        <div className="px-4 py-2">
          <div className="flex items-center gap-2 px-2 py-1.5 rounded bg-amber-500/10 border border-amber-500/30">
            <div className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
            <span className="text-[10px] font-medium text-amber-300 uppercase tracking-wide">
              Demo Data
            </span>
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 py-2 px-2 space-y-0.5 overflow-y-auto">
        {navItems.map((item) => {
          const active = isActive(item.to);
          return (
            <Link
              key={item.to}
              to={item.to}
              onClick={() => setMobileOpen(false)}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                active
                  ? 'bg-accent-blue/10 text-accent-blue border-l-2 border-accent-blue'
                  : 'text-text-secondary hover:text-text-primary hover:bg-bg-tertiary'
              }`}
              title={collapsed ? item.label : undefined}
            >
              <span className="flex-shrink-0">{item.icon}</span>
              {!collapsed && <span>{item.label}</span>}
              {item.badge && !collapsed && (
                <span className="ml-auto text-[10px] px-1.5 py-0.5 rounded bg-accent-blue/20 text-accent-blue">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Collapse Toggle */}
      <div className="border-t border-border-default p-2">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="hidden lg:flex items-center justify-center w-full px-3 py-2 rounded-md text-text-tertiary hover:text-text-primary hover:bg-bg-tertiary transition-colors"
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <ChevronLeft className={`w-4 h-4 transition-transform ${collapsed ? 'rotate-180' : ''}`} />
          {!collapsed && <span className="ml-2 text-xs">Collapse</span>}
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Mobile sidebar */}
      <div
        className={`fixed top-0 left-0 h-full w-64 bg-bg-secondary border-r border-border-default z-50 transform transition-transform lg:hidden ${
          mobileOpen ? 'translate-x-0' : '-translate-x-64'
        }`}
      >
        <div className="flex items-center justify-between px-4 h-14 border-b border-border-default">
          <span className="text-sm font-bold text-text-primary">HHGOA</span>
          <button
            onClick={() => setMobileOpen(false)}
            className="p-1.5 rounded-md text-text-tertiary hover:text-text-primary hover:bg-bg-tertiary"
            aria-label="Close menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <NavContent />
      </div>

      {/* Desktop sidebar */}
      <aside
        className={`hidden lg:flex flex-col fixed top-0 left-0 h-full bg-bg-secondary border-r border-border-default z-30 transition-all duration-200 ${
          collapsed ? 'w-16' : 'w-64'
        }`}
      >
        <NavContent />
      </aside>

      {/* Mobile menu button */}
      <button
        onClick={() => setMobileOpen(true)}
        className="lg:hidden fixed top-3 left-3 z-40 p-2 rounded-md bg-bg-secondary border border-border-default text-text-secondary"
        aria-label="Open menu"
      >
        <Menu className="w-5 h-5" />
      </button>
    </>
  );
};