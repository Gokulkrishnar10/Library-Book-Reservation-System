import React from 'react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts'

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload
    return (
      <div
        style={{
          background: 'rgba(15, 23, 42, 0.95)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '8px',
          padding: '0.75rem 1rem',
          boxShadow: '0 8px 24px rgba(0, 0, 0, 0.5)',
          backdropFilter: 'blur(8px)',
        }}
      >
        <p style={{ fontWeight: 700, fontSize: '0.875rem', color: '#f8fafc', marginBottom: '0.4rem' }}>
          {data.fullTitle}
        </p>
        <p style={{ fontSize: '0.8125rem', color: '#10b981', margin: '0.2rem 0' }}>
          ● Available: <strong>{data.available}</strong>
        </p>
        <p style={{ fontSize: '0.8125rem', color: '#f59e0b', margin: '0.2rem 0' }}>
          ● Reserved: <strong>{data.reserved}</strong>
        </p>
        <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.4rem', borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '0.3rem' }}>
          Total Copies: {data.total}
        </p>
      </div>
    )
  }
  return null
}

export default function AvailabilityChart({ books }) {
  if (!books || books.length === 0) return null

  const chartData = books.map((b) => ({
    name: b.title.length > 16 ? b.title.substring(0, 14) + '…' : b.title,
    fullTitle: b.title,
    available: b.available_copies,
    reserved: Math.max(0, b.total_copies - b.available_copies),
    total: b.total_copies,
  }))

  return (
    <div className="glass-panel" id="availability-chart-container">
      <div className="chart-header">
        <h2 className="section-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--primary)' }}>
            <line x1="18" y1="20" x2="18" y2="10" />
            <line x1="12" y1="20" x2="12" y2="4" />
            <line x1="6" y1="20" x2="6" y2="14" />
          </svg>
          Real-Time Inventory & Reservation Breakdown
        </h2>
        <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
          Updated live
        </span>
      </div>

      <div style={{ width: '100%', height: 260 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 15, left: -20, bottom: 25 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" vertical={false} />
            <XAxis
              dataKey="name"
              stroke="#64748b"
              fontSize={12}
              tickLine={false}
              interval={0}
              angle={-20}
              textAnchor="end"
            />
            <YAxis
              stroke="#64748b"
              fontSize={12}
              tickLine={false}
              allowDecimals={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              verticalAlign="top"
              align="right"
              iconType="circle"
              wrapperStyle={{ paddingBottom: '12px', fontSize: '12px' }}
            />
            <Bar dataKey="available" name="Available Copies" stackId="inventory" fill="#10b981" radius={[0, 0, 4, 4]} />
            <Bar dataKey="reserved" name="Reserved Copies" stackId="inventory" fill="#f59e0b" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
