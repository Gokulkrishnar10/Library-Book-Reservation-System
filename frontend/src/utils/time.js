export function formatCountdown(expiresAtStr) {
  const exp = new Date(expiresAtStr)
  const diff = exp - Date.now()
  if (diff <= 0) return 'Expired'
  const d = Math.floor(diff / 86400000)
  const h = Math.floor((diff % 86400000) / 3600000)
  const m = Math.floor((diff % 3600000) / 60000)
  if (d > 0) return `${d}d ${h}h`
  if (h > 0) return `${h}h ${m}m`
  return `${m}m`
}

export function isExpiringSoon(expiresAtStr) {
  const diff = new Date(expiresAtStr) - Date.now()
  return diff > 0 && diff < 24 * 3600 * 1000 // < 24h
}
