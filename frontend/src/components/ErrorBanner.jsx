import React, { useEffect } from 'react'

export default function ErrorBanner({ message, onDismiss }) {
  useEffect(() => {
    if (!message) return
    // Auto-dismiss after 6 seconds so user doesn't have stale errors
    const timer = setTimeout(() => {
      onDismiss()
    }, 6000)
    return () => clearTimeout(timer)
  }, [message, onDismiss])

  if (!message) return null

  return (
    <aside className="error-banner" id="error-banner" role="alert" aria-live="assertive">
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
        <div style={{
          background: 'rgba(239, 68, 68, 0.2)',
          borderRadius: '50%',
          padding: '6px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0
        }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f87171" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <strong style={{ fontSize: '0.875rem', color: '#fca5a5', fontWeight: 600 }}>Action Failed</strong>
          <span style={{ fontSize: '0.84rem', color: '#fecaca', lineHeight: 1.4 }}>{message}</span>
        </div>
      </div>
      <button
        id="error-banner-dismiss"
        className="error-close-btn"
        onClick={onDismiss}
        aria-label="Dismiss error"
        title="Dismiss notification"
      >
        &times;
      </button>
    </aside>
  )
}
