import React from 'react';
import { Search, Bell, ChevronDown, LogOut, User, Settings } from 'lucide-react';
import { isDemoMode } from '@/config';
import { TigerGraphUnavailable } from '@/components/ui/States';

interface TopBarProps {
  onSearch?: (query: string) => void;
}

export const TopBar: React.FC<TopBarProps> = ({ onSearch }) => {
  const [searchOpen, setSearchOpen] = React.useState(false);
  const [searchQuery, setSearchQuery] = React.useState('');
  const [profileOpen, setProfileOpen] = React.useState(false);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    onSearch?.(e.target.value);
  };

  return (
    <header className="fixed top-0 right-0 h-14 bg-bg-secondary/95 backdrop-blur-sm border-b border-border-default z-20 flex items-center gap-3 px-4">
      {/* Left spacer for sidebar offset - handled by CSS grid */}

      {/* Global Search */}
      <div className="relative flex-1 max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-tertiary" />
        <input
          type="text"
          placeholder="Search investigations, cases, customers..."
          value={searchQuery}
          onChange={handleSearch}
          onFocus={() => setSearchOpen(true)}
          onBlur={() => setTimeout(() => setSearchOpen(false), 200)}
          className="w-full pl-9 pr-3 py-2 text-sm bg-bg-tertiary border border-border-default rounded-md text-text-primary placeholder-text-tertiary focus:outline-none focus:border-accent-blue focus:ring-1 focus:ring-accent-blue"
        />
        {searchOpen && searchQuery && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-bg-secondary border border-border-default rounded-md shadow-lg py-1 z-50">
            <div className="px-3 py-2 text-xs text-text-tertiary">
              Press Enter to search across all investigations
            </div>
          </div>
        )}
      </div>

      {/* System Status */}
      <div className="hidden sm:flex items-center gap-2 px-2.5 py-1.5 rounded-md bg-bg-tertiary border border-border-default">
        <div className="w-2 h-2 rounded-full bg-status-resolved" />
        <span className="text-xs text-text-secondary">System</span>
      </div>

      {isDemoMode() && <TigerGraphUnavailable />}

      {/* Notifications */}
      <button
        className="relative p-2 rounded-md text-text-secondary hover:text-text-primary hover:bg-bg-tertiary transition-colors"
        aria-label="Notifications"
      >
        <Bell className="w-5 h-5" />
        <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-risk-critical" />
      </button>

      {/* User Menu */}
      <div className="relative">
        <button
          onClick={() => setProfileOpen(!profileOpen)}
          className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-bg-tertiary transition-colors"
        >
          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-accent-blue to-blue-700 flex items-center justify-center">
            <User className="w-4 h-4 text-white" />
          </div>
          <ChevronDown className="w-4 h-4 text-text-tertiary hidden sm:block" />
        </button>

        {profileOpen && (
          <div
            className="absolute top-full right-0 mt-1 w-48 bg-bg-secondary border border-border-default rounded-md shadow-lg py-1 z-50"
            onMouseLeave={() => setProfileOpen(false)}
          >
            <div className="px-3 py-2 border-b border-border-default">
              <p className="text-sm font-medium text-text-primary">Analyst Demo</p>
              <p className="text-xs text-text-tertiary">demo@hhgoa.internal</p>
            </div>
            <button className="flex items-center gap-2 w-full px-3 py-2 text-sm text-text-secondary hover:text-text-primary hover:bg-bg-tertiary">
              <User className="w-4 h-4" /> Profile
            </button>
            <button className="flex items-center gap-2 w-full px-3 py-2 text-sm text-text-secondary hover:text-text-primary hover:bg-bg-tertiary">
              <Settings className="w-4 h-4" /> Settings
            </button>
            <div className="border-t border-border-default my-1" />
            <button className="flex items-center gap-2 w-full px-3 py-2 text-sm text-text-secondary hover:text-text-primary hover:bg-bg-tertiary">
              <LogOut className="w-4 h-4" /> Sign out
            </button>
          </div>
        )}
      </div>
    </header>
  );
};