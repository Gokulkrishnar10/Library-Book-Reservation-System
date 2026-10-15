import React, { useState } from 'react'
import { registerUser, loginUser, forgotPassword } from '../api'
import { extractError } from '../utils/errors'

export default function AuthModal({ isOpen, onClose, onLoginSuccess }) {
  const [mode, setMode] = useState('login') // 'login' | 'register' | 'forgot'
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [successInfo, setSuccessInfo] = useState(null)

  if (!isOpen) return null

  const resetForm = () => {
    setError(null)
    setSuccessInfo(null)
  }

  const switchMode = (newMode) => {
    resetForm()
    setMode(newMode)
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccessInfo(null)
    try {
      const res = await registerUser(name, email)
      setSuccessInfo({
        title: 'Account Created Successfully!',
        message: res.message,
        password: res.dev_password_preview,
        action: 'login',
      })
      if (res.dev_password_preview) {
        setPassword(res.dev_password_preview)
      }
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await loginUser(email, password)
      onLoginSuccess(res.user, res.token)
      onClose()
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }

  const handleForgot = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccessInfo(null)
    try {
      const res = await forgotPassword(email)
      setSuccessInfo({
        title: 'Password Reset Dispatched!',
        message: res.message,
        password: res.dev_password_preview,
        action: 'login',
      })
      if (res.dev_password_preview) {
        setPassword(res.dev_password_preview)
      }
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-dialog glass-panel" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close-btn" onClick={onClose} aria-label="Close modal">
          ✕
        </button>

        {/* Modal Header */}
        <div className="modal-header">
          <div className="modal-icon-badge">
            {mode === 'login' && '🔐'}
            {mode === 'register' && '✨'}
            {mode === 'forgot' && '🔄'}
          </div>
          <h2 className="modal-title">
            {mode === 'login' && 'Sign In to Library'}
            {mode === 'register' && 'Create Patron Account'}
            {mode === 'forgot' && 'Reset Your Password'}
          </h2>
          <p className="modal-subtitle">
            {mode === 'login' && 'Enter your registered Gmail and 8-character password'}
            {mode === 'register' && 'Provide your name & Gmail to receive an 8-character password'}
            {mode === 'forgot' && 'We will generate & email you a new 8-character password'}
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="modal-alert modal-alert-error">
            <span>⚠️ {error}</span>
          </div>
        )}

        {/* Success / Generated Password Highlight */}
        {successInfo && (
          <div className="modal-alert modal-alert-success">
            <h4 style={{ margin: '0 0 6px 0', fontWeight: 700 }}>{successInfo.title}</h4>
            <p style={{ margin: '0 0 10px 0', fontSize: '0.875rem' }}>{successInfo.message}</p>
            {successInfo.password ? (
              <div className="password-display-card">
                <span className="password-label">Generated 8-Character Password:</span>
                <div className="password-value-row">
                  <code className="password-code">{successInfo.password}</code>
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={() => {
                      navigator.clipboard.writeText(successInfo.password)
                      alert('Password copied to clipboard!')
                    }}
                  >
                    Copy
                  </button>
                </div>
              </div>
            ) : (
              <div style={{
                background: 'rgba(99, 102, 241, 0.15)',
                border: '1px solid rgba(99, 102, 241, 0.35)',
                borderRadius: '8px',
                padding: '0.85rem 1rem',
                margin: '10px 0',
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
              }}>
                <span style={{ fontSize: '1.5rem' }}>📬</span>
                <div style={{ fontSize: '0.8125rem', color: '#e2e8f0', lineHeight: 1.4 }}>
                  <strong>Check your Gmail:</strong> Open your Gmail inbox for <strong>{email}</strong> to find your 8-character password. Use it along with your Gmail address to sign in below!
                </div>
              </div>
            )}
            <button
              type="button"
              className="btn btn-primary btn-sm"
              style={{ marginTop: '10px', width: '100%' }}
              onClick={() => {
                setSuccessInfo(null)
                setMode('login')
              }}
            >
              Proceed to Sign In →
            </button>
          </div>
        )}

        {/* Forms */}
        {!successInfo && (
          <>
            {mode === 'login' && (
              <form onSubmit={handleLogin} className="auth-form">
                <div className="form-group">
                  <label htmlFor="login-email">Gmail Address</label>
                  <input
                    id="login-email"
                    type="email"
                    className="form-input"
                    placeholder="patron@gmail.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>

                <div className="form-group">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <label htmlFor="login-password">8-Character Password</label>
                    <button
                      type="button"
                      className="link-button"
                      onClick={() => switchMode('forgot')}
                    >
                      Forgot Password?
                    </button>
                  </div>
                  <input
                    id="login-password"
                    type="text"
                    className="form-input"
                    placeholder="e.g. K9#mX2$p"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>

                <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
                  {loading ? 'Authenticating…' : 'Sign In'}
                </button>

                <div className="auth-switch-prompt">
                  <span>Don't have an account?</span>{' '}
                  <button type="button" className="link-button" onClick={() => switchMode('register')}>
                    Register here
                  </button>
                </div>
              </form>
            )}

            {mode === 'register' && (
              <form onSubmit={handleRegister} className="auth-form">
                <div className="form-group">
                  <label htmlFor="reg-name">Full Name</label>
                  <input
                    id="reg-name"
                    type="text"
                    className="form-input"
                    placeholder="e.g. Alice Smith"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="reg-email">Gmail Address</label>
                  <input
                    id="reg-email"
                    type="email"
                    className="form-input"
                    placeholder="patron@gmail.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                  <small className="form-help-text">
                    An automated 8-character password will be sent to this email.
                  </small>
                </div>

                <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
                  {loading ? 'Creating Account…' : 'Generate Password & Register'}
                </button>

                <div className="auth-switch-prompt">
                  <span>Already registered?</span>{' '}
                  <button type="button" className="link-button" onClick={() => switchMode('login')}>
                    Sign In instead
                  </button>
                </div>
              </form>
            )}

            {mode === 'forgot' && (
              <form onSubmit={handleForgot} className="auth-form">
                <div className="form-group">
                  <label htmlFor="forgot-email">Registered Gmail Address</label>
                  <input
                    id="forgot-email"
                    type="email"
                    className="form-input"
                    placeholder="patron@gmail.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                  <small className="form-help-text">
                    We will generate a new 8-character password and dispatch it immediately.
                  </small>
                </div>

                <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
                  {loading ? 'Issuing Reset…' : 'Email New Password'}
                </button>

                <div className="auth-switch-prompt">
                  <button type="button" className="link-button" onClick={() => switchMode('login')}>
                    ← Back to Sign In
                  </button>
                </div>
              </form>
            )}
          </>
        )}
      </div>
    </div>
  )
}
