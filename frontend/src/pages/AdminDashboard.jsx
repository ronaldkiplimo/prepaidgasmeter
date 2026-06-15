import { useEffect, useState } from 'react'
import { adminAPI } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'

export default function AdminDashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    adminAPI.dashboard()
      .then((res) => setStats(res.data))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner />
  if (!stats) return <p>Failed to load dashboard.</p>

  const statCards = [
    { label: 'Total Users', value: stats.users.total },
    { label: 'Active Meters', value: stats.meters.total },
    { label: 'Total Revenue', value: `KES ${stats.revenue.total}` },
    { label: "Today's Revenue", value: `KES ${stats.revenue.today}` },
    { label: 'Completed Txns', value: stats.transactions.completed },
    { label: 'Failed Txns', value: stats.transactions.failed },
    { label: 'Pending Txns', value: stats.transactions.pending },
    { label: 'Tokens Generated', value: stats.tokens.total_generated },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-500">Platform overview and monitoring</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {statCards.map((s) => (
          <div key={s.label} className="card">
            <p className="text-sm text-gray-500">{s.label}</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{s.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Recent Transactions</h2>
          <div className="space-y-2">
            {stats.recent_transactions.map((t, i) => (
              <div key={i} className="flex justify-between text-sm p-2 bg-gray-50 rounded">
                <span>{t.reference} · {t.user__phone_number}</span>
                <span className="font-medium">KES {t.amount}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Recent Audit Logs</h2>
          <div className="space-y-2">
            {stats.recent_audit_logs.map((l, i) => (
              <div key={i} className="flex justify-between text-sm p-2 bg-gray-50 rounded">
                <span>{l.action}</span>
                <span className="text-gray-500">{l.user__phone_number}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
