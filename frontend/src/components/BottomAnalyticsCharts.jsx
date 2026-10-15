import React, { useMemo } from 'react'
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts'

const GENRE_COLORS = {
  Fiction: '#6366f1',
  Mystery: '#8b5cf6',
  Science: '#06b6d4',
  Technology: '#10b981',
  Horror: '#f43f5e',
  Comedy: '#f59e0b',
  Philosophy: '#ec4899',
  Fantasy: '#3b82f6',
  General: '#64748b',
}

const PALETTE = [
  '#6366f1', '#06b6d4', '#10b981', '#f59e0b',
  '#f43f5e', '#8b5cf6', '#ec4899', '#3b82f6',
]

export default function BottomAnalyticsCharts({ books }) {
  if (!books || books.length === 0) return null

  // 1. Data for Chart A: Books by Genre Distribution (Donut)
  const genreData = useMemo(() => {
    const counts = {}
    books.forEach((b) => {
      const gRaw = b.genre || 'General'
      const parts = gRaw.split(',').map((s) => s.trim()).filter(Boolean)
      if (parts.length === 0) parts.push('General')
      parts.forEach((g) => {
        counts[g] = (counts[g] || 0) + 1
      })
    })
    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .map(([genre, count], idx) => ({
        name: genre,
        value: count,
        color: GENRE_COLORS[genre] || PALETTE[idx % PALETTE.length],
      }))
  }, [books])

  // 2. Data for Chart B: Top 5 In-Demand Books (Horizontal Bar Chart)
  const demandData = useMemo(() => {
    return [...books]
      .map((b) => {
        const reserved = Math.max(0, b.total_copies - b.available_copies)
        return {
          id: b.id,
          title: b.title,
          shortTitle: b.title.length > 20 ? b.title.substring(0, 18) + '…' : b.title,
          reserved,
          available: b.available_copies,
          total: b.total_copies,
        }
      })
      .sort((a, b) => b.reserved - a.reserved || b.total - a.total)
      .slice(0, 5)
  }, [books])

  return (
    <section className="bottom-charts-section" id="analytics-section">
      <div className="section-header-banner">
        <div>
          <h2 className="section-title">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--primary)' }}>
              <path d="M21.21 15.89A10 10 0 1 1 8 2.83" />
              <path d="M22 12A10 10 0 0 0 12 2v10z" />
            </svg>
            Live Library Analytics & Catalog Intelligence
          </h2>
          <p className="section-subtitle">Real-time inventory segmentation and high-demand title rankings</p>
        </div>
      </div>

      <div className="charts-grid-row">
        {/* Chart A: Books by Genre Distribution (Donut) */}
        <div className="glass-panel chart-card" id="genre-distribution-chart">
          <div className="chart-header">
            <h3 className="chart-card-title">
              <span>📚</span> Catalog Distribution by Genre
            </h3>
            <span className="badge badge-info">{genreData.length} Genres Active</span>
          </div>

          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={genreData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={95}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {genreData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: 'rgba(15, 23, 42, 0.95)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '8px',
                    color: '#f8fafc',
                  }}
                  formatter={(val, name) => [`${val} Books`, `${name}`]}
                />
                <Legend
                  verticalAlign="bottom"
                  height={36}
                  iconType="circle"
                  wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart B: Top 5 In-Demand Books (Horizontal Bar Chart) */}
        <div className="glass-panel chart-card" id="top-demand-chart">
          <div className="chart-header">
            <h3 className="chart-card-title">
              <span>🔥</span> Top 5 Most In-Demand Titles
            </h3>
            <span className="badge badge-warning">Active Holds</span>
          </div>

          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={demandData}
                margin={{ top: 10, right: 30, left: 10, bottom: 10 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" horizontal={false} />
                <XAxis type="number" stroke="#64748b" fontSize={11} allowDecimals={false} />
                <YAxis
                  type="category"
                  dataKey="shortTitle"
                  stroke="#94a3b8"
                  fontSize={11}
                  width={110}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{
                    background: 'rgba(15, 23, 42, 0.95)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '8px',
                    color: '#f8fafc',
                  }}
                  formatter={(val, name, item) => [
                    `${val} reserved (${item.payload.available} available / ${item.payload.total} total)`,
                    item.payload.title,
                  ]}
                />
                <Bar
                  dataKey="reserved"
                  name="Active Reservations"
                  fill="#f59e0b"
                  radius={[0, 4, 4, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </section>
  )
}
