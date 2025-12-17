/**
 * Configuration centralisée - Facade Suite
 */

// Backend API URL (FastAPI)
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Supabase Configuration (injectée via environment variables)
export const SUPABASE_CONFIG = {
  url: import.meta.env.VITE_SUPABASE_URL,
  anonKey: import.meta.env.VITE_SUPABASE_ANON_KEY,
}

// Debug mode
export const DEBUG = import.meta.env.DEV
