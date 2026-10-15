import React, { useState, useEffect, useRef } from 'react'
import { getNotifications, markNotificationRead, markAllNotificationsRead } from '../api'

export default function NotificationBell({ currentUser }) {
  const [notifications, setNotifications] = useState([])
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef(null)

  const fetchNotifications = async () => {
    if (!currentUser?.email) return
    try {
      const data = await getNotifications(currentUser.email, currentUser.name)
      setNotifications(data || [])
    } catch (err) {
      console.warn('Failed to fetch in-app notifications:', err)
    }
  }

  // Poll every 8 seconds when user is logged in
  useEffect(() => {
    fetchNotifications()
    const interval = setInterval(fetchNotifications, 8000)
    return () => clearInterval(interval)
  }, [currentUser])

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false)
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen])

  const unreadCount = notifications.filter((n) => !n.is_read).length

  const handleMarkRead = async (id, e) => {
    e.stopPropagation()
    try {
      await markNotificationRead(id)
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      )
    } catch (err) {
      console.error('Failed to mark notification read:', err)
    }
  }

  const handleMarkAllRead = async () => {
    if (!currentUser?.email) return
    try {
      await markAllNotificationsRead(currentUser.email)
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })))
    } catch (err) {
      console.error('Failed to mark all read:', err)
    }
  }

  if (!currentUser) return null

  return (
    <div className="notification-bell-wrapper" ref={dropdownRef} style={{ position: 'relative' }}>
      <button
        id="notification-bell-btn"
        className="notification-bell-btn"
        onClick={() => setIsOpen(!isOpen)}
        title="View in-app notifications"
        aria-label="In-app notifications"
        style={{
          position: 'relative',
          background: isOpen ? 'rgba(99, 102, 241, 0.25)' : 'rgba(255, 255, 255, 0.08)',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          borderRadius: '50%',
          width: '38px',
          height: '38px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          color: '#ffffff',
          transition: 'all 0.2s ease',
        }}
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
          <path d="M13.73 21a2 2 0 0 1-3.46 0" />
        </svg>

        {unreadCount > 0 && (
          <span
            id="notification-badge"
            style={{
              position: 'absolute',
              top: '-3px',
              right: '-3px',
              background: '#ef4444',
              color: '#ffffff',
              fontSize: '0.65rem',
              fontWeight: 800,
              borderRadius: '9999px',
              minWidth: '18px',
              height: '18px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '0 4px',
              boxShadow: '0 0 8px rgba(239, 68, 68, 0.6)',
              animation: 'pulse 1.5s infinite',
            }}
          >
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Notifications Dropdown */}
      {isOpen && (
        <div
          className="notification-dropdown glass-panel"
          style={{
            position: 'absolute',
            top: 'calc(100% + 10px)',
            right: 0,
            width: '340px',
            maxHeight: '420px',
            overflowY: 'auto',
            zIndex: 10000,
            background: 'rgba(15, 23, 42, 0.95)',
            backdropFilter: 'blur(16px)',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            borderRadius: '12px',
            boxShadow: '0 16px 36px rgba(0, 0, 0, 0.5), 0 0 20px rgba(99, 102, 241, 0.2)',
            padding: '0.75rem',
          }}
        >
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              paddingBottom: '0.6rem',
              borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
              marginBottom: '0.5rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ fontSize: '0.875rem', fontWeight: 700, color: '#f8fafc' }}>
                Notifications
              </span>
              {unreadCount > 0 && (
                <span style={{
                  fontSize: '0.7rem',
                  background: 'rgba(239, 68, 68, 0.2)',
                  color: '#f87171',
                  padding: '1px 6px',
                  borderRadius: '10px',
                  fontWeight: 600,
                }}>
                  {unreadCount} unread
                </span>
              )}
            </div>
            {unreadCount > 0 && (
              <button
                type="button"
                onClick={handleMarkAllRead}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#818cf8',
                  fontSize: '0.75rem',
                  cursor: 'pointer',
                  padding: '2px 4px',
                }}
              >
                Mark all read
              </button>
            )}
          </div>

          {notifications.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '1.5rem 0', color: 'var(--text-muted)', fontSize: '0.8125rem' }}>
              <span style={{ fontSize: '1.5rem', display: 'block', marginBottom: '0.35rem' }}>🔕</span>
              No notifications yet.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {notifications.map((notif) => (
                <div
                  key={notif.id}
                  onClick={(e) => !notif.is_read && handleMarkRead(notif.id, e)}
                  style={{
                    padding: '0.65rem 0.75rem',
                    borderRadius: '8px',
                    background: notif.is_read ? 'rgba(255, 255, 255, 0.03)' : 'rgba(99, 102, 241, 0.12)',
                    border: notif.is_read ? '1px solid rgba(255, 255, 255, 0.05)' : '1px solid rgba(99, 102, 241, 0.3)',
                    cursor: notif.is_read ? 'default' : 'pointer',
                    transition: 'all 0.2s ease',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.2rem' }}>
                    <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: notif.is_read ? '#cbd5e1' : '#ffffff' }}>
                      {notif.title}
                    </span>
                    {!notif.is_read && (
                      <span style={{
                        width: '7px',
                        height: '7px',
                        borderRadius: '50%',
                        background: '#38bdf8',
                        marginTop: '4px',
                      }} />
                    )}
                  </div>
                  <p style={{ fontSize: '0.775rem', color: notif.is_read ? '#94a3b8' : '#e2e8f0', margin: '0 0 0.35rem 0', lineHeight: 1.35 }}>
                    {notif.message}
                  </p>
                  <span style={{ fontSize: '0.6875rem', color: '#64748b' }}>
                    {new Date(notif.created_at).toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
