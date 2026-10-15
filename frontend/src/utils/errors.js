export function extractError(err) {
  if (!err.response) return 'Cannot reach the server'
  const detail = err.response.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map((e) => e.msg).join('; ')
  return `Error ${err.response.status}`
}
