import React, { useState, useCallback, useEffect } from 'react'
import { listBooks, getUserReservations } from './api'
import { usePolling } from './hooks/usePolling'
import { extractError } from './utils/errors'
import ErrorBanner from './components/ErrorBanner'
import FilterBar from './components/FilterBar'
import BookList from './components/BookList'
import BottomAnalyticsCharts from './components/BottomAnalyticsCharts'
import AuthModal from './components/AuthModal'
import AdminPortal from './components/AdminPortal'
import AiAssistant from './components/AiAssistant'
import NotificationBell from './components/NotificationBell'
import UserProfileModal from './components/UserProfileModal'
import LogoutConfirmModal from './components/LogoutConfirmModal'

export default function App() {
  const [books, setBooks] = useState([])
  const [error, setError] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedGenre, setSelectedGenre] = useState('')
  const [showAvailableOnly, setShowAvailableOnly] = useState(false)
  const [initialLoaded, setInitialLoaded] = useState(false)

  // AI Librarian Filter & Highlight state
  const [aiFilteredBookIds, setAiFilteredBookIds] = useState(null)
  const [aiQueryText, setAiQueryText] = useState('')
  const [highlightedBookId, setHighlightedBookId] = useState(null)

  // Active reservations held by the current user
  const [userReservedBookIds, setUserReservedBookIds] = useState([])

  // Auth, View & Modal state
  const [currentUser, setCurrentUser] = useState(null)
  const [authModalOpen, setAuthModalOpen] = useState(false)
  const [userProfileOpen, setUserProfileOpen] = useState(false)
  const [logoutConfirmOpen, setLogoutConfirmOpen] = useState(false)
  const [currentView, setCurrentView] = useState('catalog') // 'catalog' | 'admin'

  // Restore session from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem('library_user')
      if (stored) {
        setCurrentUser(JSON.parse(stored))
      }
    } catch (e) {
      console.error('Failed to parse stored session:', e)
    }
  }, [])

  const handleLoginSuccess = (user, token) => {
    setCurrentUser(user)
    try {
      localStorage.setItem('library_user', JSON.stringify(user))
      localStorage.setItem('library_token', token)
    } catch (e) {
      console.error('Failed to store session:', e)
    }
    if (user?.name) {
      getUserReservations(user.name).then((resList) => {
        setUserReservedBookIds((resList || []).map((r) => r.book_id))
      }).catch(() => {})
    }
  }

  const handleLogout = () => {
    setCurrentUser(null)
    setUserReservedBookIds([])
    localStorage.removeItem('library_user')
    localStorage.removeItem('library_token')
    localStorage.removeItem('last_reserved_user_name')
    if (currentView === 'admin') {
      setCurrentView('catalog')
    }
  }

  const fetchBooks = useCallback(async () => {
    try {
      const data = await listBooks(selectedGenre)
      setBooks(data)
      setInitialLoaded(true)
    } catch (err) {
      setError(extractError(err))
    }
  }, [selectedGenre])

  const fetchUserReservationsList = useCallback(async () => {
    const activeName = currentUser?.name || localStorage.getItem('last_reserved_user_name')
    if (!activeName) {
      setUserReservedBookIds([])
      return
    }
    try {
      const resList = await getUserReservations(activeName)
      const ids = (resList || []).map((r) => r.book_id)
      setUserReservedBookIds(ids)
    } catch (e) {
      // Ignore silent errors
    }
  }, [currentUser])

  const handleReserveSuccess = useCallback(async (reservedUserName, reservedBookId) => {
    if (reservedUserName) {
      try {
        localStorage.setItem('last_reserved_user_name', reservedUserName)
      } catch (e) {}
    }
    if (reservedBookId) {
      setUserReservedBookIds((prev) => Array.from(new Set([...prev, reservedBookId])))
    }
    await fetchBooks()
    await fetchUserReservationsList()
  }, [fetchBooks, fetchUserReservationsList])

  const handleAiRecommendation = useCallback((bookIds, queryText) => {
    if (bookIds && bookIds.length > 0) {
      setAiFilteredBookIds(bookIds)
      setAiQueryText(queryText || '')
      setCurrentView('catalog')
    } else {
      setAiFilteredBookIds(null)
      setAiQueryText('')
    }
  }, [])

  const handleClearAiFilter = useCallback(() => {
    setAiFilteredBookIds(null)
    setAiQueryText('')
  }, [])

  const handleHighlightBook = useCallback((bookId) => {
    setHighlightedBookId(bookId)
    setTimeout(() => {
      const el = document.getElementById(`book-card-${bookId}`)
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }, 120)
    setTimeout(() => {
      setHighlightedBookId((curr) => (curr === bookId ? null : curr))
    }, 3500)
  }, [])

  // Poll books & user active reservations every 5 seconds (5000ms) with immediate first tick
  const pollAll = useCallback(async () => {
    await fetchBooks()
    await fetchUserReservationsList()
  }, [fetchBooks, fetchUserReservationsList])

  usePolling(pollAll, 5000)

  return (
    <div className="app-layout">
      {/* Header */}
      <header className="app-header">
        <div className="brand-wrapper" onClick={() => setCurrentView('catalog')} style={{ cursor: 'pointer' }}>
          <div className="brand-logo">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
            </svg>
          </div>
          <div>
            <h1 className="brand-title">Library Book Reservation System</h1>
            <p className="brand-subtitle">Real-time inventory tracking, AI assistant & automated notifications</p>
          </div>
        </div>

        {/* Right Header: Auth, Notifications & Indicators */}
        <div className="header-right-actions">
          {currentUser?.role === 'admin' && (
            <button
              className={`btn btn-sm ${currentView === 'admin' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setCurrentView(currentView === 'admin' ? 'catalog' : 'admin')}
            >
              {currentView === 'admin' ? '📖 Catalog View' : '⚙️ Admin Console'}
            </button>
          )}

          {/* In-App Notification Bell */}
          <NotificationBell currentUser={currentUser} />

          {currentUser ? (
            <div className="user-profile-badge">
              <div
                style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', cursor: 'pointer' }}
                onClick={() => setUserProfileOpen(true)}
                title="Click to view My Profile & Active Reservations"
              >
                <span className="user-avatar-circle">
                  {currentUser.name.charAt(0).toUpperCase()}
                </span>
                <div className="user-info-text">
                  <span className="user-name-label">{currentUser.name}</span>
                  <span className="user-role-label">{currentUser.role.toUpperCase()}</span>
                </div>
              </div>
              <button
                className="btn-logout"
                onClick={() => setLogoutConfirmOpen(true)}
                title="Log Out of Session"
              >
                Log Out
              </button>
            </div>
          ) : (
            <button
              className="btn btn-primary btn-sm"
              onClick={() => setAuthModalOpen(true)}
            >
              🔐 Sign In / Register
            </button>
          )}

          <div className="live-indicator">
            <span className="pulse-dot"></span>
            <span>Live 5s Polling</span>
          </div>
        </div>
      </header>

      {/* Dismissable Fixed Floating Error Toast */}
      <ErrorBanner
        message={error}
        onDismiss={() => setError(null)}
      />

      {/* Main View Switching */}
      {currentView === 'admin' ? (
        <AdminPortal onBackToCatalog={() => setCurrentView('catalog')} />
      ) : (
        <>
          {/* Multi-Genre Filter and Search Bar */}
          <FilterBar
            query={searchQuery}
            onQuery={setSearchQuery}
            availOnly={showAvailableOnly}
            onAvailOnly={setShowAvailableOnly}
            selectedGenre={selectedGenre}
            onSelectGenre={setSelectedGenre}
          />

          {/* AI Librarian Recommendations Filter Banner */}
          {aiFilteredBookIds !== null && (
            <div className="ai-catalog-filter-banner">
              <div className="ai-banner-content">
                <span className="ai-banner-icon">🤖</span>
                <div className="ai-banner-text">
                  <div className="ai-banner-title">
                    <span>AI Librarian Recommendations Active</span>
                    <span className="ai-banner-badge">{aiFilteredBookIds.length} recommended</span>
                  </div>
                  {aiQueryText && (
                    <p className="ai-banner-subtitle">
                      Matching your query: &ldquo;<em>{aiQueryText}</em>&rdquo;
                    </p>
                  )}
                </div>
              </div>
              <button
                className="btn btn-secondary btn-sm ai-banner-reset-btn"
                onClick={handleClearAiFilter}
                title="Clear AI recommendation filter and display all catalog books"
              >
                ✕ Show All Books
              </button>
            </div>
          )}

          {/* Main Books Grid */}
          <BookList
            books={books}
            query={searchQuery}
            availOnly={showAvailableOnly}
            selectedGenre={selectedGenre}
            aiFilteredBookIds={aiFilteredBookIds}
            highlightedBookId={highlightedBookId}
            userReservedBookIds={userReservedBookIds}
            currentUser={currentUser}
            onReserveSuccess={handleReserveSuccess}
            onError={(msg) => setError(msg)}
          />

          {/* Bottom Analytics & Charts (Genre Donut + Horizontal Bar) */}
          <BottomAnalyticsCharts books={books} />
        </>
      )}

      {/* AI Voice Librarian Widget */}
      <AiAssistant
        onAiRecommendation={handleAiRecommendation}
        onHighlightBook={handleHighlightBook}
      />

      {/* Auth Modal (Login / Register / Forgot Password) */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onLoginSuccess={handleLoginSuccess}
      />

      {/* Patron Profile & Active Reservations Modal */}
      <UserProfileModal
        isOpen={userProfileOpen}
        onClose={() => setUserProfileOpen(false)}
        currentUser={currentUser}
        onReservationUpdated={pollAll}
      />

      {/* Logout Confirmation Prompt Modal */}
      <LogoutConfirmModal
        isOpen={logoutConfirmOpen}
        onCancel={() => setLogoutConfirmOpen(false)}
        onConfirm={() => {
          setLogoutConfirmOpen(false)
          handleLogout()
        }}
      />
    </div>
  )
}
