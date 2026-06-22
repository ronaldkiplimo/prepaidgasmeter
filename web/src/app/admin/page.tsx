'use client'

import { useQuery } from '@tanstack/react-query'
import { AppShell } from '@/components/app-shell'
import { StatCard } from '@/components/ui'
import { adminApi } from '@/lib/api'

export default function AdminDashboardPage() {
  const { data: analytics } = useQuery({ queryKey: ['analytics'], queryFn: () => adminApi.analytics().then((r) => r.data) })
  const { data: dashboard } = useQuery({ queryKey: ['admin-dashboard'], queryFn: () => adminApi.dashboard().then((r) => r.data) })

  const stats = analytics || {}

  return (
    <AppShell>
      <h1 className="mb-8 text-2xl font-bold">Admin Dashboard</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Revenue" value={`KES ${stats.total_revenue || 0}`} />
        <StatCard label="Today" value={`KES ${stats.today_revenue || 0}`} accent="text-gas-green" />
        <StatCard label="Customers" value={stats.total_customers || 0} />
        <StatCard label="Active Meters" value={stats.active_meters || 0} />
        <StatCard label="Offline Meters" value={stats.offline_meters || 0} />
        <StatCard label="Gas Sold (units)" value={stats.gas_sold_units || 0} />
        <StatCard label="Failed Txns" value={stats.failed_transactions || 0} />
        <StatCard label="Pending" value={stats.pending_transactions || 0} />
      </div>
    </AppShell>
  )
}
