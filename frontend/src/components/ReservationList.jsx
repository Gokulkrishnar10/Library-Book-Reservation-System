import React from 'react'
import { formatCountdown, isExpiringSoon } from '../utils/time'

export default function ReservationList({ reservations, currentUser, onCancel }) {
  if (!reservations || reservations.length === 0) {
    return (
      <div style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', padding: '0.5rem 0' }}>
        No active reservations for this book.
      </div>
    )
  }

  return (
    <div className="reservation-items">
      {reservations.map((res) => {
        const expiring = isExpiringSoon(res.expires_at)
        const countdownText = formatCountdown(res.expires_at)

        // Only Admin or the patron who created the reservation can cancel it
        const isOwner =
          currentUser?.name &&
          res.user_name.toLowerCase().trim() === currentUser.name.toLowerCase().trim()
        const isAdmin = currentUser?.role === 'admin'
        const canCancel = isAdmin || isOwner

        return (
          <div key={res.id} className="reservation-item" id={`reservation-item-${res.id}`}>
            <div>
              <div className="reservation-user">
                {res.user_name}
                {isOwner && (
                  <span style={{
                    fontSize: '0.6875rem',
                    marginLeft: '0.5rem',
                    background: 'rgba(99, 102, 241, 0.2)',
                    color: '#818cf8',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    fontWeight: 600,
                  }}>
                    (You)
                  </span>
                )}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Reserved: {new Date(res.reservation_date).toLocaleDateString()}
              </div>
            </div>

            <div className="reservation-details">
              <span
                className={`countdown-badge ${expiring ? 'expiring-soon' : ''}`}
                title={`Expires at: ${new Date(res.expires_at).toLocaleString()}`}
              >
                ⏱ {countdownText}
              </span>

              {canCancel ? (
                <button
                  id={`cancel-btn-${res.id}`}
                  className="btn btn-danger"
                  onClick={() => onCancel(res.id)}
                  title={isAdmin && !isOwner ? 'Cancel reservation (as Admin)' : 'Cancel your reservation'}
                >
                  Cancel
                </button>
              ) : (
                <span
                  style={{
                    fontSize: '0.75rem',
                    color: 'var(--text-muted)',
                    padding: '0.25rem 0.5rem',
                    background: 'rgba(255, 255, 255, 0.04)',
                    borderRadius: '4px',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                  }}
                  title="Only the reservation holder or an administrator can cancel this hold"
                >
                  🔒 Held
                </span>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
