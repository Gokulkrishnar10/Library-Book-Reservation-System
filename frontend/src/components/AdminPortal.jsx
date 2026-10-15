import React, { useState, useEffect } from 'react'
import { getAdminMetrics, getAdminAuditLogs, getAdminUsers, getAdminWaitlist } from '../api'

export default function AdminPortal({ onBackToCatalog }) {
  const [metrics, setMetrics] = useState(null)
  const [auditLogs, setAuditLogs] = useState([])
  const [users, setUsers] = useState([])
  const [waitlist, setWaitlist] = useState([])
  const [activeTab, setActiveTab] = useState('audit') // 'audit' | 'users' | 'waitlist'
  const [loading, setLoading] = useState(true)

  const loadData = async () => {
    setLoading(true)
    try {
      const [m, a, u, w] = await Promise.all([
        getAdminMetrics(),
        getAdminAuditLogs(),
        getAdminUsers(),
        getAdminWaitlist(),
      ])
      setMetrics(m)
      setAuditLogs(a)
      setUsers(u)
      setWaitlist(w)
    } catch (err) {
      console.error('Error loading admin data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  return (
    <div className="admin-portal-container">
      {/* Admin Top Navigation */}
      <div className="admin-header-row">
        <div>
          <div className="admin-title-badge">ADMINISTRATIVE CONSOLE</div>
          <h1 className="brand-title" style={{ marginTop: '4px' }}>System Audit & Inventory Intelligence</h1>
          <p className="brand-subtitle">Audit trails, patron login logs, waitlist queues, and database metrics</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn btn-secondary" onClick={loadData} disabled={loading}>
            🔄 {loading ? 'Refreshing…' : 'Refresh Data'}
          </button>
          <button className="btn btn-primary" onClick={onBackToCatalog}>
            ← Back to Catalog
          </button>
        </div>
      </div>

      {/* Telemetry KPI Cards */}
      {metrics && (
        <div className="kpi-grid">
          <div className="kpi-card glass-panel">
            <span className="kpi-icon">📚</span>
            <div className="kpi-value">{metrics.total_books}</div>
            <div className="kpi-label">Titles in Catalog</div>
          </div>
          <div className="kpi-card glass-panel">
            <span className="kpi-icon">📦</span>
            <div className="kpi-value">{metrics.total_copies}</div>
            <div className="kpi-label">Total Physical Copies</div>
          </div>
          <div className="kpi-card glass-panel">
            <span className="kpi-icon">✅</span>
            <div className="kpi-value" style={{ color: '#10b981' }}>{metrics.available_copies}</div>
            <div className="kpi-label">Available on Shelf</div>
          </div>
          <div className="kpi-card glass-panel">
            <span className="kpi-icon">⏳</span>
            <div className="kpi-value" style={{ color: '#f59e0b' }}>{metrics.active_reservations}</div>
            <div className="kpi-label">Active Reservations</div>
          </div>
          <div className="kpi-card glass-panel">
            <span className="kpi-icon">👥</span>
            <div className="kpi-value" style={{ color: '#6366f1' }}>{metrics.total_users}</div>
            <div className="kpi-label">Registered Patrons</div>
          </div>
          <div className="kpi-card glass-panel">
            <span className="kpi-icon">🔔</span>
            <div className="kpi-value" style={{ color: '#ec4899' }}>{metrics.total_waitlist_pending}</div>
            <div className="kpi-label">Pending Waitlists</div>
          </div>
        </div>
      )}

      {/* Admin Tabs */}
      <div className="admin-tabs-nav">
        <button
          className={`admin-tab-btn ${activeTab === 'audit' ? 'active' : ''}`}
          onClick={() => setActiveTab('audit')}
        >
          📜 Live Audit Trail ({auditLogs.length})
        </button>
        <button
          className={`admin-tab-btn ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          👤 Patrons & Login Timestamps ({users.length})
        </button>
        <button
          className={`admin-tab-btn ${activeTab === 'waitlist' ? 'active' : ''}`}
          onClick={() => setActiveTab('waitlist')}
        >
          🔔 Restock Waitlist Queue ({waitlist.length})
        </button>
      </div>

      {/* Tab 1: Audit Logs */}
      {activeTab === 'audit' && (
        <div className="glass-panel admin-table-container">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Event Type</th>
                <th>Patron / User Email</th>
                <th>Details</th>
                <th>Timestamp (UTC)</th>
              </tr>
            </thead>
            <tbody>
              {auditLogs.length === 0 ? (
                <tr>
                  <td colSpan="4" style={{ textAlign: 'center', color: '#94a3b8', padding: '24px' }}>
                    No audit records logged yet.
                  </td>
                </tr>
              ) : (
                auditLogs.map((log) => (
                  <tr key={log.id}>
                    <td>
                      <span className={`event-badge event-${log.event_type.toLowerCase()}`}>
                        {log.event_type}
                      </span>
                    </td>
                    <td style={{ fontWeight: 500, color: '#e2e8f0' }}>{log.user_email || '—'}</td>
                    <td>{log.details}</td>
                    <td style={{ color: '#94a3b8', fontSize: '0.8125rem' }}>
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Tab 2: Users & Login Timestamps */}
      {activeTab === 'users' && (
        <div className="glass-panel admin-table-container">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email Address</th>
                <th>Role</th>
                <th>Registered At</th>
                <th>Last Login Time</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td style={{ fontWeight: 600, color: '#f8fafc' }}>{u.name}</td>
                  <td>{u.email}</td>
                  <td>
                    <span className={`badge ${u.role === 'admin' ? 'badge-primary' : 'badge-secondary'}`}>
                      {u.role.toUpperCase()}
                    </span>
                  </td>
                  <td style={{ color: '#94a3b8', fontSize: '0.8125rem' }}>
                    {new Date(u.created_at).toLocaleDateString()}
                  </td>
                  <td style={{ color: u.last_login_at ? '#10b981' : '#64748b', fontSize: '0.8125rem' }}>
                    {u.last_login_at ? new Date(u.last_login_at).toLocaleString() : 'Never'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Tab 3: Waitlist Queue */}
      {activeTab === 'waitlist' && (
        <div className="glass-panel admin-table-container">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Book ID</th>
                <th>Patron Email</th>
                <th>Status</th>
                <th>Requested Date</th>
                <th>Notified Date</th>
              </tr>
            </thead>
            <tbody>
              {waitlist.length === 0 ? (
                <tr>
                  <td colSpan="5" style={{ textAlign: 'center', color: '#94a3b8', padding: '24px' }}>
                    No pending waitlists.
                  </td>
                </tr>
              ) : (
                waitlist.map((w) => (
                  <tr key={w.id}>
                    <td><strong>#{w.book_id}</strong></td>
                    <td>{w.user_email}</td>
                    <td>
                      <span className={`badge ${w.status === 'notified' ? 'badge-success' : 'badge-warning'}`}>
                        {w.status.toUpperCase()}
                      </span>
                    </td>
                    <td style={{ color: '#94a3b8', fontSize: '0.8125rem' }}>
                      {new Date(w.created_at).toLocaleString()}
                    </td>
                    <td style={{ color: '#94a3b8', fontSize: '0.8125rem' }}>
                      {w.notified_at ? new Date(w.notified_at).toLocaleString() : 'Pending Restock'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
