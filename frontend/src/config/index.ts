// HHGOA Frontend Configuration
//
// API base URL is resolved centrally in src/services/api-client.ts.
// Importing that module here guarantees a single resolution order:
//   1. VITE_API_BASE_URL  (production: deployed Render backend)
//   2. '/'                (local dev: Vite proxies to localhost:8000)
import { API_BASE_URL } from '@/services/api-client';

export const CONFIG = {
  DEMO_MODE: true,
  APP_NAME: 'HHGOA Fraud Intelligence',
  APP_VERSION: '1.0.0',
  API_BASE_URL,
  TIGERGRAPH_URL: import.meta.env.VITE_TIGERGRAPH_URL || '',
  TIGERGRAPH_MCP_URL: import.meta.env.VITE_TIGERGRAPH_MCP_URL || '',
  REFRESH_INTERVAL_MS: 30000,
  MAX_EVIDENCE_ITEMS: 100,
  MAX_GRAPH_NODES: 50,
  RISK_SCORE_THRESHOLD_HIGH: 70,
  RISK_SCORE_THRESHOLD_MEDIUM: 40,
} as const;

export function isDemoMode(): boolean {
  return CONFIG.DEMO_MODE;
}