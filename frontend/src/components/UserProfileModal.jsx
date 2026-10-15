import React, { useState, useEffect } from 'react'
import { getUserReservations, cancelReservation } from '../api'
import { formatCountdown, isExpiringSoon } from '../utils/time'
import { extractError } from '../utils/errors'

export default function UserProfileModal({ isOpen, onClose, currentUser, onReservationUpdated }) {
  const [reservations, setReservations] = useState([])
  const [loading, setLoading] = useState(false)
  const [actionError, setActionError] = useState(null)
  const [cancellingId, setCancellingId] = useState(null)

  const fetchUserReservations = async () => {
    if (!currentUser?.name) return
    try {
      setLoading(true)
      setActionError(null)
      const data = await getUserReservations(currentUser.name)
      setReservations(data || [])
    } catch (err) {
      setActionError(extractError(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isOpen && currentUser) {
      fetchUserReservations()
    }
  }, [isOpen, currentUser])

  const handleCancel = async (resId) => {
    try {
      setCancellingId(resId)
      await cancelReservation(resId, currentUser.name, currentUser.role)
      // Refresh user's list
      await fetchUserReservations()
      // Notify parent app so main catalog also refreshes available copies
      if (onReservationUpdated) {
        onReservationUpdated()
      }
    } catch (err) {
      setActionError(extractError(err))
    } finally {
      setCancellingId(null)
    }
  }

  if (!isOpen || !currentUser) return null

  return (
    <div className="modal-backdrop" onClick={onClose} style={{
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
    }}>
      <div
        className="modal-card glass-panel"
        onClick={(e) => e.stopPropagation()}
        style={{
          width: '100%',
          maxWidth: '560px',
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          background: 'rgba(15, 23, 42, 0.98)',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          borderRadius: '16px',
          boxShadow: '0 24px 48px rgba(0, 0, 0, 0.6), 0 0 32px rgba(99, 102, 241, 0.25)',
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <div style={{
          padding: '1.25rem 1.5rem',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
            <span style={{
              width: '44px',
              height: '44px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #6366f1, #a855f7)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.25rem',
              fontWeight: 700,
              color: '#ffffff',
              boxShadow: '0 0 16px rgba(99, 102, 241, 0.4)',
            }}>
              {currentUser.name.charAt(0).toUpperCase()}
            </span>
            <div>
              <h2 style={{ fontSize: '1.125rem', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
                {currentUser.name}
              </h2>
              <span style={{ fontSize: '0.8125rem', color: '#94a3b8' }}>
                {currentUser.email} · <span style={{ textTransform: 'uppercase', color: '#818cf8', fontWeight: 600 }}>{currentUser.role}</span>
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'rgba(255, 255, 255, 0.06)',
              border: 'none',
              color: '#94a3b8',
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              cursor: 'pointer',
              fontSize: '1.1rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            ✕
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: '1.5rem', overflowY: 'auto', flex: 1 }}>
          {actionError && (
            <div style={{
              padding: '0.75rem 1rem',
              background: 'rgba(239, 68, 68, 0.2)',
              border: '1px solid rgba(239, 68, 68, 0.4)',
              color: '#fca5a5',
              borderRadius: '8px',
              fontSize: '0.8125rem',
              marginBottom: '1rem',
            }}>
              {actionError}
            </div>
          )}

          {/* Active Reservations Section */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '1rem',
          }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f1f5f9', margin: 0 }}>
              📖 My Active Reservations
            </h3>
            <span style={{
              fontSize: '0.75rem',
              fontWeight: 700,
              padding: '3px 10px',
              borderRadius: '9999px',
              background: reservations.length > 0 ? 'rgba(99, 102, 241, 0.25)' : 'rgba(255, 255, 255, 0.08)',
              color: reservations.length > 0 ? '#a5b4fc' : '#94a3b8',
              border: '1px solid rgba(99, 102, 241, 0.3)',
            }}>
              {reservations.length} {reservations.length === 1 ? 'Book Held' : 'Books Held'}
            </span>
          </div>

          {loading ? (
            <div style={{ textAlign: 'center', padding: '2rem 0', color: '#94a3b8', fontSize: '0.875rem' }}>
              Loading your reservations…
            </div>
          ) : reservations.length === 0 ? (
            <div style={{
              textAlign: 'center',
              padding: '2.5rem 1.5rem',
              background: 'rgba(255, 255, 255, 0.02)',
              borderRadius: '12px',
              border: '1px dashed rgba(255, 255, 255, 0.1)',
            }}>
              <span style={{ fontSize: '2.5rem', display: 'block', marginBottom: '0.5rem' }}>📚</span>
              <p style={{ color: '#cbd5e1', fontWeight: 600, fontSize: '0.95rem', margin: '0 0 0.25rem 0' }}>
                You have no active reservations right now.
              </p>
              <p style={{ color: '#64748b', fontSize: '0.8125rem', margin: 0 }}>
                Browse our catalog of over 200 books across 8 genres and reserve titles anytime!
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {reservations.map((res) => {
                const expiring = isExpiringSoon(res.expires_at)
                const countdown = formatCountdown(res.expires_at)
                const isCancelling = cancellingId === res.id

                return (
                  <div
                    key={res.id}
                    style={{
                      padding: '1rem',
                      background: 'rgba(255, 255, 255, 0.04)',
                      border: '1px solid rgba(255, 255, 255, 0.08)',
                      borderRadius: '10px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      gap: '1rem',
                    }}
                  >
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                        <span style={{
                          fontSize: '0.6875rem',
                          background: 'rgba(99, 102, 241, 0.2)',
                          color: '#818cf8',
                          padding: '2px 6px',
                          borderRadius: '4px',
                          fontWeight: 600,
                        }}>
                          {res.book_genre}
                        </span>
                        <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                          Reserved {new Date(res.reservation_date).toLocaleDateString()}
                        </span>
                      </div>
                      <h4 style={{
                        fontSize: '0.95rem',
                        fontWeight: 600,
                        color: '#f8fafc',
                        margin: '0 0 0.2rem 0',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                      }}>
                        {res.book_title}
                      </h4>
                      <p style={{ fontSize: '0.8125rem', color: '#94a3b8', margin: 0 }}>
                        by {res.book_author}
                      </p>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.45rem', flexShrink: 0 }}>
                      <span
                        className={`countdown-badge ${expiring ? 'expiring-soon' : ''}`}
                        title={`Hold expires at: ${new Date(res.expires_at).toLocaleString()}`}
                        style={{ fontSize: '0.75rem' }}
                      >
                        ⏱ {countdown}
                      </span>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleCancel(res.id)}
                        disabled={isCancelling}
                        style={{ fontSize: '0.75rem', padding: '0.3rem 0.65rem' }}
                      >
                        {isCancelling ? 'Cancelling…' : 'Cancel Hold'}
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: '1rem 1.5rem',
          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
          background: 'rgba(0, 0, 0, 0.2)',
          display: 'flex',
          justifyContent: 'flex-end',
        }}>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
