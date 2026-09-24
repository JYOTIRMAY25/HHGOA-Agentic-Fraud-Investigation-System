// HHGOA Backend API Client
//
// Single source of truth for the backend base URL.
//
// Resolution order:
//   1. VITE_API_BASE_URL  (production: the deployed Render backend)
//   2. '/'                (local dev: Vite proxies /investigate & /health
//                         to the backend on localhost:8000)
//
// Never hardcode a localhost URL here — it must come from the environment.
const FALLBACK = '/';

function resolveBaseUrl(): string {
  const raw = import.meta.env.VITE_API_BASE_URL as string | undefined;
  if (raw && raw.trim().length > 0) {
    return raw.trim().replace(/\/+$/, '');
  }
  return FALLBACK;
}

export const API_BASE_URL: string = resolveBaseUrl();

export function apiPath(path: string): string {
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${p}`;
}