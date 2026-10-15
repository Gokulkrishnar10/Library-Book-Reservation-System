import { useEffect, useRef } from 'react'

export function usePolling(fn, intervalMs) {
  const pending = useRef(false)
  useEffect(() => {
    let id
    const tick = async () => {
      if (pending.current) return
      pending.current = true
      try {
        await fn()
      } finally {
        pending.current = false
      }
    }
    tick()
    id = setInterval(tick, intervalMs)
    return () => clearInterval(id)
  }, [fn, intervalMs])
}
