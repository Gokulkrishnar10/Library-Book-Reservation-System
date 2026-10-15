import React from 'react'

export default function LogoutConfirmModal({ isOpen, onCancel, onConfirm }) {
  if (!isOpen) return null

  return (
    <div
      className="modal-backdrop"
      onClick={onCancel}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(8px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 100000,
        padding: '1rem',
      }}
    >
      <div
        className="modal-card glass-panel"
        onClick={(e) => e.stopPropagation()}
        style={{
          width: '100%',
          maxWidth: '420px',
          background: 'rgba(15, 23, 42, 0.98)',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          borderRadius: '16px',
          boxShadow: '0 24px 48px rgba(0, 0, 0, 0.6), 0 0 32px rgba(239, 68, 68, 0.2)',
          padding: '1.75rem',
          textAlign: 'center',
        }}
      >
        <div style={{
          width: '56px',
          height: '56px',
          borderRadius: '50%',
          background: 'rgba(239, 68, 68, 0.15)',
          border: '1px solid rgba(239, 68, 68, 0.35)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 1.25rem auto',
          fontSize: '1.5rem',
        }}>
          🚪
        </div>

        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc', marginBottom: '0.5rem' }}>
          Log Out of Session?
        </h3>
        <p style={{ fontSize: '0.875rem', color: '#94a3b8', lineHeight: 1.5, marginBottom: '1.75rem' }}>
          Are you sure you want to end your current library session? You can sign back in anytime using your credentials.
        </p>

        <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onCancel}
            style={{ flex: 1, padding: '0.65rem' }}
          >
            Stay Signed In
          </button>
          <button
            type="button"
            className="btn btn-danger"
            onClick={onConfirm}
            style={{ flex: 1, padding: '0.65rem' }}
          >
            Yes, Log Out
          </button>
        </div>
      </div>
    </div>
  )
}
