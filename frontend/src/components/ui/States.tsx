import React from 'react';
import { AlertTriangle, Loader2, FileX, ServerOff, SearchX } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
  icon?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ title, description, action, icon }) => (
  <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
    <div className="w-14 h-14 rounded-full bg-bg-tertiary border border-border-default flex items-center justify-center mb-4">
      {icon || <FileX className="w-7 h-7 text-text-tertiary" />}
    </div>
    <h3 className="text-base font-semibold text-text-primary mb-1">{title}</h3>
    {description && <p className="text-sm text-text-secondary max-w-sm mb-4">{description}</p>}
    {action}
  </div>
);

export const LoadingState: React.FC<{ message?: string }> = ({ message = 'Loading...' }) => (
  <div className="flex flex-col items-center justify-center py-12">
    <Loader2 className="w-8 h-8 text-accent-blue animate-spin mb-3" />
    <p className="text-sm text-text-secondary">{message}</p>
  </div>
);

export const ErrorState: React.FC<{ title?: string; message?: string; onRetry?: () => void }> = ({
  title = 'Something went wrong',
  message,
  onRetry,
}) => (
  <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
    <div className="w-14 h-14 rounded-full bg-risk-critical/10 border border-risk-critical/30 flex items-center justify-center mb-4">
      <AlertTriangle className="w-7 h-7 text-risk-critical" />
    </div>
    <h3 className="text-base font-semibold text-text-primary mb-1">{title}</h3>
    {message && <p className="text-sm text-text-secondary max-w-sm mb-4">{message}</p>}
    {onRetry && (
      <button
        onClick={onRetry}
        className="px-4 py-2 rounded-md bg-accent-blue/10 hover:bg-accent-blue/20 text-accent-blue text-sm font-medium transition-colors focus-ring"
      >
        Try again
      </button>
    )}
  </div>
);

export const NoSearchResults: React.FC<{ query?: string }> = ({ query }) => (
  <EmptyState
    title="No results found"
    description={query ? `No investigations match "${query}"` : 'Try adjusting your search or filters'}
    icon={<SearchX className="w-7 h-7 text-text-tertiary" />}
  />
);

export const TigerGraphUnavailable: React.FC = () => (
  <div className="flex items-center gap-2 px-3 py-2 rounded-md bg-amber-500/10 border border-amber-500/30">
    <ServerOff className="w-4 h-4 text-amber-400" />
    <span className="text-xs text-amber-300 font-medium">TigerGraph Offline</span>
  </div>
);