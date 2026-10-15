import React, { useState, useEffect, useRef } from 'react'
import { askAiLibrarian } from '../api'

export default function AiAssistant({ onAiRecommendation, onHighlightBook }) {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: 'Hello! I am your AI Librarian. Ask me for book recommendations across genres, or click the microphone to speak with me!',
    },
  ])
  const [inputQuery, setInputQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [speechEnabled, setSpeechEnabled] = useState(true)

  const messagesEndRef = useRef(null)
  const recognitionRef = useRef(null)
  const silenceTimerRef = useRef(null)
  const currentTranscriptRef = useRef('')

  // Initialize Web Speech Recognition with 3.0s pause tolerance
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition()
      recognition.continuous = true
      recognition.interimResults = true
      recognition.lang = 'en-US'

      recognition.onstart = () => {
        setIsListening(true)
        currentTranscriptRef.current = ''
      }

      recognition.onend = () => {
        setIsListening(false)
        if (silenceTimerRef.current) {
          clearTimeout(silenceTimerRef.current)
        }
      }

      recognition.onerror = (err) => {
        console.warn('Speech recognition error:', err)
        setIsListening(false)
        if (silenceTimerRef.current) {
          clearTimeout(silenceTimerRef.current)
        }
      }

      recognition.onresult = (event) => {
        let fullTranscript = ''
        for (let i = 0; i < event.results.length; i++) {
          fullTranscript += event.results[i][0].transcript + ' '
        }
        fullTranscript = fullTranscript.trim()
        currentTranscriptRef.current = fullTranscript
        setInputQuery(fullTranscript)

        // Reset silence debounce timer on every spoken syllable
        if (silenceTimerRef.current) {
          clearTimeout(silenceTimerRef.current)
        }

        // Auto-submit after 3.0 seconds of silence
        silenceTimerRef.current = setTimeout(() => {
          if (recognitionRef.current) {
            try {
              recognitionRef.current.stop()
            } catch (e) {
              // Ignore if already stopped
            }
          }
          if (currentTranscriptRef.current.trim()) {
            handleSendQuery(currentTranscriptRef.current.trim())
            currentTranscriptRef.current = ''
          }
        }, 3000)
      }

      recognitionRef.current = recognition
    }
  }, [])

  // Auto-scroll chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const speakText = (text) => {
    if (!speechEnabled || !window.speechSynthesis) return
    window.speechSynthesis.cancel() // Stop any ongoing speech
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = 1.0
    utterance.pitch = 1.0
    window.speechSynthesis.speak(utterance)
  }

  const handleSendQuery = async (queryToSend) => {
    const q = (queryToSend || inputQuery).trim()
    if (!q || loading) return

    setInputQuery('')
    setMessages((prev) => [...prev, { sender: 'user', text: q }])
    setLoading(true)

    try {
      const res = await askAiLibrarian(q)
      const botReply = res.response || "Here are some books from our catalog that match your interest!"
      const recBooks = res.recommended_books || []
      const recIds = res.recommended_book_ids || []

      // Automatically filter the catalog on the main page
      if (onAiRecommendation && recIds.length > 0) {
        onAiRecommendation(recIds, q)
      }

      setMessages((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: botReply,
          recommendedBooks: recBooks,
        },
      ])
      speakText(botReply)
    } catch (err) {
      const errMsg = 'Sorry, I had trouble reaching the catalog recommendation service. Please try again!'
      setMessages((prev) => [...prev, { sender: 'bot', text: errMsg }])
    } finally {
      setLoading(false)
    }
  }

  const toggleMic = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari!')
      return
    }
    if (isListening) {
      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current)
      }
      try {
        recognitionRef.current.stop()
      } catch (e) {
        // Ignore
      }
      if (currentTranscriptRef.current.trim()) {
        handleSendQuery(currentTranscriptRef.current.trim())
        currentTranscriptRef.current = ''
      }
    } else {
      try {
        currentTranscriptRef.current = ''
        setInputQuery('')
        recognitionRef.current.start()
      } catch (e) {
        console.error('Failed to start speech recognition:', e)
      }
    }
  }

  return (
    <div className="ai-assistant-container">
      {/* Floating Trigger Button */}
      {!isOpen && (
        <button
          className="ai-floating-trigger-btn"
          onClick={() => setIsOpen(true)}
          aria-label="Open AI Librarian"
        >
          <span className="ai-btn-icon">🎙️</span>
          <span className="ai-btn-text">AI Voice Librarian</span>
          <span className="ai-pulse-ring"></span>
        </button>
      )}

      {/* Expanded Chat Widget */}
      {isOpen && (
        <div className="ai-chat-window glass-panel">
          {/* Header */}
          <div className="ai-chat-header">
            <div className="ai-header-left">
              <span className="ai-avatar">🤖</span>
              <div>
                <h3 className="ai-header-title">AI Librarian & Voice Assistant</h3>
                <span className="ai-header-sub">Powered by Groq Cloud AI</span>
              </div>
            </div>
            <div className="ai-header-actions">
              <button
                type="button"
                className={`ai-toggle-sound-btn ${speechEnabled ? 'active' : ''}`}
                onClick={() => setSpeechEnabled(!speechEnabled)}
                title={speechEnabled ? 'Mute Speech' : 'Enable Voice Speech'}
              >
                {speechEnabled ? '🔊 Voice ON' : '🔇 Muted'}
              </button>
              <button
                type="button"
                className="ai-close-btn"
                onClick={() => {
                  setIsOpen(false)
                  if (window.speechSynthesis) window.speechSynthesis.cancel()
                  if (isListening && recognitionRef.current) {
                    try { recognitionRef.current.stop() } catch (e) {}
                  }
                }}
              >
                ✕
              </button>
            </div>
          </div>

          {/* Active Listening Status Indicator */}
          {isListening && (
            <div style={{
              background: 'linear-gradient(90deg, rgba(239, 68, 68, 0.2), rgba(99, 102, 241, 0.2))',
              borderBottom: '1px solid rgba(239, 68, 68, 0.3)',
              padding: '0.45rem 1rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: '0.75rem',
              color: '#fca5a5',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: '#ef4444',
                  animation: 'pulse 1s infinite',
                }} />
                <span>Listening… speak freely (auto-submits after 3s pause)</span>
              </div>
              <button
                type="button"
                onClick={toggleMic}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#ffffff',
                  textDecoration: 'underline',
                  cursor: 'pointer',
                  fontSize: '0.72rem',
                }}
              >
                Done Speaking
              </button>
            </div>
          )}

          {/* Chat Messages */}
          <div className="ai-messages-list">
            {messages.map((m, idx) => (
              <div key={idx} className={`ai-message-row ai-msg-${m.sender}`}>
                {m.sender === 'bot' && <span className="ai-msg-avatar">📚</span>}
                <div className="ai-message-bubble">
                  <div className="ai-bubble-text">{m.text}</div>
                  {m.recommendedBooks && m.recommendedBooks.length > 0 && (
                    <div className="ai-chat-recommendations">
                      <div className="ai-chat-rec-header">
                        <span>🎯 Filtered in Catalog (click to view):</span>
                      </div>
                      <div className="ai-chat-chips-list">
                        {m.recommendedBooks.map((bk) => (
                          <button
                            key={bk.id}
                            type="button"
                            className="ai-chat-book-chip"
                            onClick={() => onHighlightBook && onHighlightBook(bk.id)}
                            title={`Scroll to "${bk.title}" in catalog`}
                          >
                            <span className="ai-chip-title">📖 {bk.title}</span>
                            <span className="ai-chip-arrow">↗</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="ai-message-row ai-msg-bot">
                <span className="ai-msg-avatar">📚</span>
                <div className="ai-message-bubble ai-typing-indicator">
                  <span>Searching catalog & generating recommendation…</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Voice & Input Controls */}
          <form
            className="ai-chat-input-row"
            onSubmit={(e) => {
              e.preventDefault()
              handleSendQuery()
            }}
          >
            <button
              type="button"
              className={`ai-mic-btn ${isListening ? 'listening' : ''}`}
              onClick={toggleMic}
              title={isListening ? 'Listening… click to finish and send now' : 'Click to speak with microphone (3s pause threshold)'}
            >
              {isListening ? '🔴' : '🎙️'}
            </button>
            <input
              type="text"
              className="ai-input-field"
              placeholder={isListening ? 'Listening to your voice…' : 'Ask for recommendations...'}
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              disabled={loading}
            />
            <button
              type="submit"
              className="btn btn-primary ai-send-btn"
              disabled={loading || !inputQuery.trim()}
            >
              Send
            </button>
          </form>
        </div>
      )}
    </div>
  )
}
