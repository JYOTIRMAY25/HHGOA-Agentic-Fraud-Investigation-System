import React from 'react';

interface ToastProps {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  onClose: (id: string) => void;
}

const Toast: React.FC<ToastProps> = ({ id, message, type, onClose }) => {
  const typeStyles = {
    success: 'bg-emerald-900/90 border-emerald-500/50 text-emerald-100',
    error: 'bg-red-900/90 border-red-500/50 text-red-100',
    warning: 'bg-amber-900/90 border-amber-500/50 text-amber-100',
    info: 'bg-blue-900/90 border-blue-500/50 text-blue-100',
  };

  const icons = {
    success: '✓',
    error: '✕',
    warning: '!',
    info: 'i',
  };

  return (
    <div
      className={`flex items-center gap-2 px-4 py-3 rounded-lg border backdrop-blur-sm shadow-lg animate-[slideIn_200ms_ease-out] min-w-[280px] max-w-[420px] ${typeStyles[type]}`}
      role="alert"
    >
      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-white/10 text-sm font-bold">
        {icons[type]}
      </span>
      <span className="text-sm font-medium flex-1">{message}</span>
      <button
        onClick={() => onClose(id)}
        className="text-white/50 hover:text-white/80 transition-colors"
        aria-label="Dismiss"
      >
        ✕
      </button>
    </div>
  );
};

interface ToastProviderProps {
  children: React.ReactNode;
}

export const ToastProvider: React.FC<ToastProviderProps> = ({ children }) => {
  const [toasts, setToasts] = React.useState<ToastProps[]>([]);

  const addToast = React.useCallback((message: string, type: ToastProps['type'] = 'info', duration = 4000) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
    setToasts((prev) => [...prev, { id, message, type, duration, onClose: removeToast }]);

    if (duration > 0) {
      setTimeout(() => removeToast(id), duration);
    }
  }, []);

  const removeToast = React.useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      <div className="fixed top-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none">
        <div className="pointer-events-auto">
          {toasts.map((t) => (
            <Toast key={t.id} {...t} />
          ))}
        </div>
      </div>
    </ToastContext.Provider>
  );
};

interface ToastContextValue {
  addToast: (message: string, type?: ToastProps['type'], duration?: number) => void;
  removeToast: (id: string) => void;
}

const ToastContext = React.createContext<ToastContextValue | null>(null);

export const useToast = (): ToastContextValue => {
  const ctx = React.useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
};

export default Toast;