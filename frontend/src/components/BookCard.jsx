import React, { useState, useEffect } from 'react'
import { getBook, reserveBook, cancelReservation, joinWaitlist } from '../api'
import { extractError } from '../utils/errors'
import ReservationList from './ReservationList'

export default function BookCard({
  book,
  currentUser,
  isHighlighted = false,
  isUserReserved = false,
  onReserveSuccess,
  onError,
}) {
  const [userName, setUserName] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)
  const [reservations, setReservations] = useState([])
  const [loadingReservations, setLoadingReservations] = useState(false)
  const [localReserved, setLocalReserved] = useState(isUserReserved)

  useEffect(() => {
    setLocalReserved(isUserReserved)
  }, [isUserReserved])

  // Waitlist state
  const [showWaitlistPrompt, setShowWaitlistPrompt] = useState(false)
  const [waitlistEmail, setWaitlistEmail] = useState('')
  const [waitlistSubmitting, setWaitlistSubmitting] = useState(false)
  const [waitlistJoined, setWaitlistJoined] = useState(false)

  const isAvailable = book.available_copies > 0

  // Check if current user actively holds a reservation for this book
  const isReservedByCurrent = Boolean(
    isUserReserved ||
    localReserved ||
    (userName.trim() && reservations.some(
      (r) => r.user_name?.toLowerCase().trim() === userName.toLowerCase().trim()
    ))
  )

  // Pre-fill user name if logged in (only for patrons, leave empty for admin so admin can enter any name)
  useEffect(() => {
    if (currentUser?.role !== 'admin' && currentUser?.name && !userName) {
      setUserName(currentUser.name)
    }
    if (currentUser?.email && !waitlistEmail) {
      setWaitlistEmail(currentUser.email)
    }
  }, [currentUser])

  const loadReservations = async () => {
    try {
      setLoadingReservations(true)
      const detail = await getBook(book.id)
      setReservations(detail.reservations || [])
    } catch (err) {
      onError(extractError(err))
    } finally {
      setLoadingReservations(false)
    }
  }

  const handleToggleExpand = () => {
    const nextState = !isExpanded
    setIsExpanded(nextState)
    if (nextState) {
      loadReservations()
    }
  }

  const handleReserve = async (e) => {
    e.preventDefault()
    if (isReservedByCurrent) {
      onError("User already has an active reservation for this book")
      return
    }
    if (!userName.trim() || !isAvailable) return

    try {
      setSubmitting(true)
      await reserveBook(book.id, userName.trim())
      onError(null) // Clear any previous error toast
      setLocalReserved(true)
      if (onReserveSuccess) {
        onReserveSuccess(userName.trim(), book.id)
      }
      if (currentUser?.role === 'admin') {
        setUserName('') // Keep admin input ready for next patron entry
      }
      if (isExpanded) {
        await loadReservations()
      }
    } catch (err) {
      onError(extractError(err))
    } finally {
      setSubmitting(false)
    }
  }

  const handleCancelReservation = async (resId) => {
    try {
      await cancelReservation(resId, currentUser?.name || userName, currentUser?.role)
      onError(null)
      setLocalReserved(false)
      if (onReserveSuccess) {
        onReserveSuccess()
      }
      await loadReservations()
    } catch (err) {
      onError(extractError(err))
    }
  }

  const handleJoinWaitlist = async (e) => {
    e.preventDefault()
    if (!waitlistEmail.trim()) return

    try {
      setWaitlistSubmitting(true)
      await joinWaitlist(book.id, waitlistEmail.trim())
      setWaitlistJoined(true)
      setShowWaitlistPrompt(false)
      alert(`Success! You will receive an email at ${waitlistEmail} the instant a copy of "${book.title}" becomes available!`)
    } catch (err) {
      onError(extractError(err))
    } finally {
      setWaitlistSubmitting(false)
    }
  }

  return (
    <div
      className={`book-card ${isHighlighted ? 'ai-highlighted' : ''}`}
      id={`book-card-${book.id}`}
    >

      <div>
        {/* Genre Pill & Metadata */}
        <div className="book-meta">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '8px', marginBottom: '4px' }}>
            <h3 className="book-title" id={`book-title-${book.id}`}>{book.title}</h3>
            <span className="badge badge-genre" id={`genre-tag-${book.id}`}>
              {book.genre || 'General'}
            </span>
          </div>
          <p className="book-author" id={`book-author-${book.id}`}>by {book.author}</p>
        </div>

        {/* Stock pill */}
        <div className="inventory-badge-row">
          <span className={`stock-pill ${isAvailable ? 'in-stock' : 'out-of-stock'}`} id={`stock-pill-${book.id}`}>
            {isAvailable ? '● Available' : '○ Out of stock'}
          </span>
          <span className="stock-numbers">
            <strong id={`available-copies-${book.id}`}>{book.available_copies}</strong> of {book.total_copies} left
          </span>
        </div>

        {/* Reservation Form: Active Reservation Held vs Available */}
        {isReservedByCurrent ? (
          <form
            onSubmit={(e) => {
              e.preventDefault()
              onError("User already has an active reservation for this book")
            }}
            className="reserve-form"
          >
            <input
              id={`reserve-user-${book.id}`}
              type="text"
              className="reserve-input input-reserved"
              placeholder="Reserved by you"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              disabled={currentUser?.role !== 'admin'}
              title="You currently hold an active reservation for this book"
            />
            <button
              id={`reserve-btn-${book.id}`}
              type="button"
              className="btn btn-reserved"
              onClick={() => onError("User already has an active reservation for this book")}
              title="You already have an active reservation for this book. Click to view alert."
            >
              ✓ Reserved
            </button>
          </form>
        ) : isAvailable ? (
          <form onSubmit={handleReserve} className="reserve-form">
            <input
              id={`reserve-user-${book.id}`}
              type="text"
              className="reserve-input"
              placeholder="Enter your name to reserve..."
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              disabled={submitting}
            />
            <button
              id={`reserve-btn-${book.id}`}
              type="submit"
              className="btn btn-primary"
              disabled={submitting || !userName.trim()}
            >
              {submitting ? 'Reserving...' : 'Reserve'}
            </button>
          </form>
        ) : (
          /* Out-of-Stock: Waitlist Option */
          <div className="waitlist-card-box">
            {waitlistJoined ? (
              <div className="waitlist-success-badge">
                <span>🔔 You're on the restock notification list!</span>
              </div>
            ) : !showWaitlistPrompt ? (
              <button
                type="button"
                className="btn btn-warning btn-block"
                onClick={() => setShowWaitlistPrompt(true)}
              >
                🔔 Notify When Available
              </button>
            ) : (
              <form onSubmit={handleJoinWaitlist} className="waitlist-inline-form">
                <input
                  type="email"
                  className="reserve-input"
                  placeholder="Your Gmail address..."
                  value={waitlistEmail}
                  onChange={(e) => setWaitlistEmail(e.target.value)}
                  required
                />
                <div style={{ display: 'flex', gap: '6px' }}>
                  <button type="submit" className="btn btn-primary btn-sm" disabled={waitlistSubmitting}>
                    {waitlistSubmitting ? 'Subscribing…' : 'Subscribe'}
                  </button>
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={() => setShowWaitlistPrompt(false)}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            )}
          </div>
        )}
      </div>

      <div>
        <button
          id={`toggle-reservations-${book.id}`}
          type="button"
          className="btn-expand"
          onClick={handleToggleExpand}
        >
          {isExpanded ? '▲ Hide reservations' : `▼ View active reservations (${book.total_copies - book.available_copies})`}
        </button>

        {isExpanded && (
          <div className="reservations-drawer" id={`reservations-drawer-${book.id}`}>
            {loadingReservations ? (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', padding: '0.5rem 0' }}>
                Loading reservations...
              </div>
            ) : (
              <ReservationList
                reservations={reservations}
                currentUser={currentUser}
                onCancel={handleCancelReservation}
              />
            )}
          </div>
        )}
      </div>
    </div>
  )
}
