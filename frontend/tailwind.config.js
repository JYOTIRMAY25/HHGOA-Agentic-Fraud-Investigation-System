/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: '#0a0e14',
          secondary: '#0d1117',
          tertiary: '#111827',
          elevated: '#161b22',
        },
        border: {
          default: '#1f2937',
          hover: '#2d3748',
          focus: '#3b82f6',
        },
        text: {
          primary: '#e5e7eb',
          secondary: '#9ca3af',
          tertiary: '#6b7280',
          muted: '#4b5563',
        },
        accent: {
          blue: '#3b82f6',
          cyan: '#06b6d4',
          teal: '#14b8a6',
        },
        risk: {
          critical: '#dc2626',
          high: '#f97316',
          medium: '#fbbf24',
          low: '#22c55e',
        },
        status: {
          new: '#3b82f6',
          investigating: '#f59e0b',
          awaiting_evidence: '#8b5cf6',
          escalated: '#dc2626',
          resolved: '#10b981',
          closed: '#6b7280',
        },
        fraud: {
          red: '#ef4444',
          amber: '#f59e0b',
          emerald: '#10b981',
          blue: '#3b82f6',
          purple: '#8b5cf6',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
        '26': '6.5rem',
        '30': '7.5rem',
      },
      maxWidth: {
        '8xl': '88rem',
        '9xl': '96rem',
      },
      boxShadow: {
        'card': '0 1px 3px -1px rgba(0, 0, 0, 0.3), 0 1px 2px -1px rgba(0, 0, 0, 0.2)',
        'card-hover': '0 4px 12px -2px rgba(0, 0, 0, 0.35), 0 2px 4px -2px rgba(0, 0, 0, 0.25)',
        'panel': '0 -2px 10px -2px rgba(0, 0, 0, 0.3)',
      },
      screens: {
        xs: '480px',
      },
    },
  },
  plugins: [],
}