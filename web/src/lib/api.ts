import axios from 'axios'

const API = process.env.NEXT_PUBLIC_API_URL || ''

export const api = axios.create({
  baseURL: `${API}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
})

export function getApiErrorMessage(error: unknown, fallback: string) {
  if (!axios.isAxiosError(error)) return fallback

  const data = error.response?.data
  if (!data) return fallback
  if (typeof data === 'string') return data
  if (typeof data.detail === 'string') return data.detail

  if (typeof data === 'object') {
    const messages = Object.entries(data)
      .flatMap(([field, value]) => {
        const text = Array.isArray(value) ? value.join(' ') : String(value)
        return text ? [`${field}: ${text}`] : []
      })
    if (messages.length) return messages.join(' ')
  }

  return fallback
}

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token) config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authApi = {
  login: (phone_number: string, password: string) =>
    api.post('/auth/login/', { phone_number, password }),
  register: (data: Record<string, string>) => api.post('/auth/register/', data),
  profile: () => api.get('/auth/profile/'),
  updateProfile: (data: Record<string, string>) => api.patch('/auth/profile/', data),
}

export const metersApi = {
  list: () => api.get('/meters/'),
  create: (data: Record<string, unknown>) => api.post('/meters/', data),
  update: (id: string, data: Record<string, unknown>) => api.patch(`/meters/${id}/`, data),
  lookup: (meterNumber: string) => api.get(`/payments/meters/${meterNumber}/lookup/`),
}

export const purchaseApi = {
  preview: (data: { meter_id?: string; meter_number?: string; amount: number }) =>
    api.post('/payments/preview/', data),
  purchase: (data: { meter_id: string; amount: number; phone_number?: string }) =>
    api.post('/payments/purchase/', data),
  transactions: () => api.get('/payments/transactions/'),
}

export const tokensApi = { history: () => api.get('/tokens/history/') }

export const adminApi = {
  analytics: () => api.get('/reports/analytics/'),
  sales: (period = 'daily') => api.get(`/reports/sales/?period=${period}`),
  dashboard: () => api.get('/audit/dashboard/'),
  auditLogs: () => api.get('/audit/logs/'),
  users: () => api.get('/auth/admin/users/'),
  updateUser: (id: string, data: Record<string, unknown>) => api.patch(`/auth/admin/users/${id}/`, data),
  meters: () => api.get('/meters/'),
  transactions: () => api.get('/payments/admin/transactions/'),
}
