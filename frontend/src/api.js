import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

// Books & Reservations
export const listBooks = (genre) => {
  const params = genre ? { genre } : {}
  return api.get('/books/', { params }).then(r => r.data)
}
export const getBook = (id) => api.get(`/books/${id}`).then(r => r.data)
export const reserveBook = (id, userName) =>
  api.post(`/books/${id}/reserve`, { user_name: userName }).then(r => r.data)
export const cancelReservation = (id, requesterName, requesterRole) => {
  const params = {}
  if (requesterName) params.requester_name = requesterName
  if (requesterRole) params.requester_role = requesterRole
  return api.delete(`/reservations/${id}`, { params })
}
export const joinWaitlist = (bookId, email) =>
  api.post(`/books/${bookId}/waitlist`, { email }).then(r => r.data)
export const getUserReservations = (userName) =>
  api.get(`/reservations/user/${encodeURIComponent(userName)}`).then(r => r.data)

// Notifications
export const getNotifications = (email, name) =>
  api.get('/notifications/', { params: { email, name } }).then(r => r.data)
export const markNotificationRead = (id) =>
  api.post(`/notifications/${id}/read`).then(r => r.data)
export const markAllNotificationsRead = (email) =>
  api.post('/notifications/read-all', null, { params: { email } }).then(r => r.data)

// Authentication
export const registerUser = (name, email) =>
  api.post('/auth/register', { name, email }).then(r => r.data)
export const loginUser = (email, password) =>
  api.post('/auth/login', { email, password }).then(r => r.data)
export const forgotPassword = (email) =>
  api.post('/auth/forgot-password', { email }).then(r => r.data)

// Admin
export const getAdminMetrics = () => api.get('/admin/metrics').then(r => r.data)
export const getAdminAuditLogs = () => api.get('/admin/audit-logs').then(r => r.data)
export const getAdminUsers = () => api.get('/admin/users').then(r => r.data)
export const getAdminWaitlist = () => api.get('/admin/waitlist').then(r => r.data)

// AI Assistant
export const askAiLibrarian = (query) =>
  api.post('/ai/recommend', { query }).then(r => r.data)

