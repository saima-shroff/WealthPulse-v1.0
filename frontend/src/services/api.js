import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('wealthpulse-token')
  if (token) config.headers['Authentication-Token'] = token
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('wealthpulse-token')
      localStorage.removeItem('wealthpulse-user')
      if (window.location.pathname !== '/login') window.location.assign('/login')
    }
    return Promise.reject(error)
  },
)

export function setSession(user, token) {
  localStorage.setItem('wealthpulse-token', token)
  localStorage.setItem('wealthpulse-user', JSON.stringify(user))
}

export function clearSession() {
  localStorage.removeItem('wealthpulse-token')
  localStorage.removeItem('wealthpulse-user')
}

export function currentUser() {
  try {
    return JSON.parse(localStorage.getItem('wealthpulse-user') || 'null')
  } catch {
    return null
  }
}

export function currency(value) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 2,
  }).format(Number(value || 0))
}

export function errorMessage(error) {
  return error.response?.data?.error || 'Something went wrong. Please try again.'
}