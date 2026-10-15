import React from 'react'

const GENRE_DEFINITIONS = [
  { name: 'Horror', icon: '👻' },
  { name: 'Comedy', icon: '😄' },
  { name: 'Technology', icon: '💻' },
  { name: 'Philosophy', icon: '🧠' },
  { name: 'Science', icon: '🔬' },
  { name: 'Mystery', icon: '🔍' },
  { name: 'Fantasy', icon: '🧙' },
  { name: 'Fiction', icon: '📚' },
]

export default function FilterBar({
  query,
  onQuery,
  availOnly,
  onAvailOnly,
  selectedGenre,
  onSelectGenre,
}) {
  const activeGenres = selectedGenre
    ? selectedGenre.split(',').map((s) => s.trim()).filter(Boolean)
    : []

  const toggleGenre = (genreName) => {
    if (activeGenres.includes(genreName)) {
      const remaining = activeGenres.filter((g) => g !== genreName)
      onSelectGenre(remaining.join(','))
    } else {
      const updated = [...activeGenres, genreName]
      onSelectGenre(updated.join(','))
    }
  }

  const handleClearAll = () => {
    onSelectGenre('')
    onQuery('')
    onAvailOnly(false)
  }

  return (
    <div className="glass-panel" style={{ padding: '1.25rem 1.5rem', marginBottom: '1.75rem' }}>
      <div className="filter-bar">
        {/* Search Input */}
        <div className="search-input-wrapper">
          <svg className="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input
            id="search-input"
            type="text"
            className="search-input"
            placeholder="Search by title, author, or genre..."
            value={query}
            onChange={(e) => onQuery(e.target.value)}
          />
        </div>

        {/* Available only toggle */}
        <label className="checkbox-label" htmlFor="filter-available-only" style={{ whiteSpace: 'nowrap' }}>
          <input
            id="filter-available-only"
            type="checkbox"
            checked={availOnly}
            onChange={(e) => onAvailOnly(e.target.checked)}
          />
          <span>In-Stock Only</span>
        </label>

        {(query || availOnly || activeGenres.length > 0) && (
          <button
            className="btn btn-sm btn-secondary"
            onClick={handleClearAll}
            title="Reset search and filters"
            style={{ fontSize: '0.8125rem' }}
          >
            ✕ Reset
          </button>
        )}
      </div>

      {/* Multi-Genre Selection Pills */}
      <div className="genre-pills-container" style={{ marginTop: '1rem', paddingTop: '0.85rem', borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.6rem' }}>
          <span style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
            🏷️ Filter by Genres (select multiple to combine):
          </span>
          {activeGenres.length > 1 && (
            <span style={{ fontSize: '0.75rem', color: 'var(--primary-glow)', background: 'rgba(99, 102, 241, 0.15)', padding: '2px 8px', borderRadius: '12px' }}>
              Multi-Match Active ({activeGenres.length} selected)
            </span>
          )}
        </div>

        <div className="genre-pills-row" style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {/* All Genres Pill */}
          <button
            type="button"
            className={`genre-pill ${activeGenres.length === 0 ? 'active' : ''}`}
            onClick={() => onSelectGenre('')}
            id="genre-pill-all"
          >
            ✨ All Genres
          </button>

          {/* Individual Genre Pills */}
          {GENRE_DEFINITIONS.map((g) => {
            const isSelected = activeGenres.includes(g.name)
            return (
              <button
                key={g.name}
                type="button"
                id={`genre-pill-${g.name.toLowerCase()}`}
                className={`genre-pill ${isSelected ? 'active' : ''}`}
                onClick={() => toggleGenre(g.name)}
              >
                <span>{g.icon} {g.name}</span>
                {isSelected && <span className="genre-pill-check">✓</span>}
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}
