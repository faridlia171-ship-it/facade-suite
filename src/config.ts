/**
 * Configuration centralisée - Facade Suite
 */

import { supabase } from './lib/supabase'

// Backend API URL (FastAPI)
export const API_URL =
  import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Supabase Configuration (injectée via environment variables)
export const SUPABASE_CONFIG = {
  url: import.meta.env.VITE_SUPABASE_URL,
  anonKey: import.meta.env.VITE_SUPABASE_ANON_KEY,
}

// Debug mode
export const DEBUG = import.meta.env.DEV

/**
 * Fetch API sécurisé avec token Supabase automatiquement injecté
 */
export async function apiFetch(
  endpoint: string,
  options: RequestInit = {}
) {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  const token = session?.access_token

  return fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  })
}
