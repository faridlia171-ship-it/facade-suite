/**
 * API helper centralisé - Facade Suite
 * Injecte automatiquement le JWT Supabase
 */

import { API_URL } from '../config'

export async function apiFetch(
  endpoint: string,
  options: RequestInit = {}
) {
  const token = localStorage.getItem('access_token')

  if (!token) {
    throw new Error('Utilisateur non authentifié (token manquant)')
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...(options.headers || {}),
    },
  })

  if (response.status === 401) {
    localStorage.removeItem('access_token')
    throw new Error('Unauthorized')
  }

  return response
}
