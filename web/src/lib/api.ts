import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'

const API = process.env.NEXT_PUBLIC_API_URL || ''

type ApiErrorBody = Record<string, unknown>
type RetryableRequestConfig = InternalAxiosRequestConfig & { _retry?: boolean }

export const getApiErrorMessage = (error: unknown, defaultMessage = 'An unexpected error occurred'): string => {
  const data = axios.isAxiosError(error) ? error.response?.data : null
  if (data && typeof data === 'object') {
    const body = data as ApiErrorBody
    if (typeof body.detail === 'string') return body.detail
    if (typeof body.message === 'string') return body.message
  }

  if (data && typeof data === 'object') {
    const fieldErrors = Object.entries(data)
      .flatMap(([field, value]) => {
        const messages = Array.isArray(value) ? value : [value]
        return messages.map((message) => `${field}: ${message}`)
      })
      .filter(Boolean)

    if (fieldErrors.length) return fieldErrors.join(', ')
  }

  if (error instanceof Error) return error.message
  return defaultMessage
}

export const api = axios.create({
  baseURL: `${API}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
})

let refreshRequest: Promise<string | null> | null = null

const clearStoredAuth = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('prepaidgas-auth')
}

const redirectToLogin = () => {
  if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
    window.location.assign('/login')
  }
}

const refreshAccessToken = async (): Promise<string | null> => {
  const refresh = localStorage.getItem('refresh_token')
  if (!refresh) return null

  if (!refreshRequest) {
    refreshRequest = axios.post(`${API}/api/v1/auth/token/refresh/`, { refresh })
      .then(({ data }) => {
        localStorage.setItem('access_token', data.access)
        if (data.refresh) localStorage.setItem('refresh_token', data.refresh)
        return data.access
      })
      .finally(() => {
        refreshRequest = null
      })
  }

  return refreshRequest
}

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token) config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetryableRequestConfig | undefined
    if (error.response?.status === 401 && original && !original._retry) {
      original._retry = true
      try {
        const access = await refreshAccessToken()
        if (access) {
          original.headers = original.headers || {}
          original.headers.Authorization = `Bearer ${access}`
          return api(original)
        }
      } catch {
        clearStoredAuth()
        redirectToLogin()
      }
      clearStoredAuth()
      redirectToLogin()
    }

    return Promise.reject(error)
  }
)

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
  transaction: (reference: string) => api.get(`/payments/transactions/${reference}/`),
  retryToken: (reference: string) => api.post(`/payments/transactions/${reference}/retry-token/`),
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
  integrations: () => api.get('/system/integrations/'),
}
