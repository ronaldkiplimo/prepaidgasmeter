import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1'

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
})

let refreshRequest = null

function clearStoredAuth() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

async function refreshAccessToken() {
  const refresh = localStorage.getItem('refresh_token')
  if (!refresh) return null

  if (!refreshRequest) {
    refreshRequest = axios.post(`${API_BASE}/auth/token/refresh/`, { refresh })
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
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
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
        window.location.href = '/login'
      }
      clearStoredAuth()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/login/', { phone_number: data.phone_number, password: data.password }),
  logout: (refresh) => api.post('/auth/logout/', { refresh }),
  profile: () => api.get('/auth/profile/'),
  updateProfile: (data) => api.patch('/auth/profile/', data),
}

export const metersAPI = {
  list: () => api.get('/meters/'),
  create: (data) => api.post('/meters/', data),
  update: (id, data) => api.patch(`/meters/${id}/`, data),
  delete: (id) => api.delete(`/meters/${id}/`),
}

export const paymentsAPI = {
  purchase: (data) => api.post('/payments/purchase/', data),
  transactions: (params) => api.get('/payments/transactions/', { params }),
  transaction: (ref) => api.get(`/payments/transactions/${ref}/`),
  retryToken: (ref) => api.post(`/payments/transactions/${ref}/retry-token/`),
}

export const tokensAPI = {
  history: () => api.get('/tokens/history/'),
}

export const adminAPI = {
  dashboard: () => api.get('/audit/dashboard/'),
  transactions: (params) => api.get('/payments/admin/transactions/', { params }),
  auditLogs: (params) => api.get('/audit/logs/', { params }),
}

export default api
