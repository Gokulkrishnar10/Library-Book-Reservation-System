import React from 'react'
import BookCard from './BookCard'

export default function BookList({
  books,
  query,
  availOnly,
  selectedGenre,
  aiFilteredBookIds = null,
  highlightedBookId = null,
  userReservedBookIds = [],
  currentUser,
  onReserveSuccess,
  onError,
}) {
  const filtered = books.filter((b) => {
    // 1. AI Recommendation filter
    if (aiFilteredBookIds && aiFilteredBookIds.length > 0) {
      if (!aiFilteredBookIds.includes(b.id)) {
        return false
      }
    }

    // 2. Search query filter
    const qLower = query.toLowerCase().trim()
    const matchQuery =
      !qLower ||
      b.title.toLowerCase().includes(qLower) ||
      b.author.toLowerCase().includes(qLower) ||
      (b.genre && b.genre.toLowerCase().includes(qLower))

    // 3. Availability filter
    const matchAvail = !availOnly || b.available_copies > 0

    // 4. Genre multi-select filter
    let matchGenre = true
    if (selectedGenre && selectedGenre !== 'All Genres') {
      const selectedList = selectedGenre
        .split(',')
        .map((s) => s.trim().toLowerCase())
        .filter(Boolean)
      if (selectedList.length > 0) {
        const bookGenre = (b.genre || '').toLowerCase()
        matchGenre = selectedList.some((sg) => bookGenre.includes(sg))
      }
    }

    return matchQuery && matchAvail && matchGenre
  })

  // Prioritize books: If AI filter is active, rank by AI recommendation order;
  // otherwise rank by multi-genre match count
  const sorted = [...filtered].sort((a, b) => {
    if (aiFilteredBookIds && aiFilteredBookIds.length > 0) {
      return aiFilteredBookIds.indexOf(a.id) - aiFilteredBookIds.indexOf(b.id)
    }

    if (!selectedGenre || !selectedGenre.includes(',')) return 0
    const list = selectedGenre.split(',').map((s) => s.trim().toLowerCase()).filter(Boolean)
    const aMatches = list.filter((g) => (a.genre || '').toLowerCase().includes(g)).length
    const bMatches = list.filter((g) => (b.genre || '').toLowerCase().includes(g)).length
    return bMatches - aMatches
  })

  if (sorted.length === 0) {
    return (
      <div className="glass-panel empty-state" id="empty-books-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ margin: '0 auto 1rem', opacity: 0.5 }}>
          <circle cx="12" cy="12" r="10" />
          <line x1="8" y1="12" x2="16" y2="12" />
        </svg>
        <p style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-secondary)' }}>No books match your criteria.</p>
        <p style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>
          {aiFilteredBookIds ? 'Try clicking "Show All Books" above to clear the AI filter.' : 'Try clearing the search query or selecting a different genre.'}
        </p>
      </div>
    )
  }

  return (
    <div className="books-grid" id="books-grid">
      {sorted.map((book) => (
        <BookCard
          key={book.id}
          book={book}
          currentUser={currentUser}
          isHighlighted={highlightedBookId === book.id}
          isUserReserved={userReservedBookIds.includes(book.id)}
          onReserveSuccess={onReserveSuccess}
          onError={onError}
        />
      ))}
    </div>
  )
}
