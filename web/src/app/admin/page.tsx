'use client'

import { useQuery } from '@tanstack/react-query'
import { Activity, AlertTriangle, Gauge, TrendingUp, Users, WalletCards } from 'lucide-react'
import { AppShell } from '@/components/app-shell'
import { Card, StatCard } from '@/components/ui'
import { adminApi } from '@/lib/api'

export default function AdminDashboardPage() {
  const { data: analytics } = useQuery({ queryKey: ['analytics'], queryFn: () => adminApi.analytics().then((r) => r.data) })
  const { data: dashboard } = useQuery({ queryKey: ['admin-dashboard'], queryFn: () => adminApi.dashboard().then((r) => r.data) })

  const stats = analytics || {}

  return (
    <AppShell>
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="eyebrow">Admin operations</p>
          <h1 className="mt-1 text-3xl font-bold tracking-tight">Meter vending overview</h1>
          <p className="mt-2 max-w-2xl text-slate-500">Track revenue, assignment coverage, meter health, and token failures from one place.</p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm dark:border-slate-800 dark:bg-slate-900">
          <span className="font-semibold text-slate-900 dark:text-white">{stats.pending_transactions || 0}</span>
          <span className="ml-1 text-slate-500">pending transactions</span>
        </div>
      </div>

      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Revenue" value={`KES ${stats.total_revenue || 0}`} helper="All completed sales" />
        <StatCard label="Today" value={`KES ${stats.today_revenue || 0}`} accent="text-teal-700" helper="Current day sales" />
        <StatCard label="Customers" value={stats.total_customers || 0} helper="Registered users" />
        <StatCard label="Active Meters" value={stats.active_meters || 0} helper={`${stats.offline_meters || 0} offline`} />
        <StatCard label="Gas Sold" value={stats.gas_sold_units || 0} helper="Units vended" />
        <StatCard label="Failed Txns" value={stats.failed_transactions || 0} accent={stats.failed_transactions ? 'text-red-700' : 'text-slate-900'} helper="Needs review" />
        <StatCard label="Pending" value={stats.pending_transactions || 0} helper="Payment/token flow" />
        <StatCard label="Offline Meters" value={stats.offline_meters || 0} accent={stats.offline_meters ? 'text-amber-700' : 'text-slate-900'} helper="Telemetry status" />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card>
          <div className="mb-4 flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal-50 text-teal-700"><TrendingUp className="h-5 w-5" /></span>
            <div>
              <h2 className="font-semibold">Vending Health</h2>
              <p className="text-sm text-slate-500">Revenue and token completion</p>
            </div>
          </div>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span className="text-slate-500">Successful sales</span><span className="font-semibold">{stats.completed_transactions || 0}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Failed sales</span><span className="font-semibold text-red-700">{stats.failed_transactions || 0}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Pending queue</span><span className="font-semibold">{stats.pending_transactions || 0}</span></div>
          </div>
        </Card>
        <Card>
          <div className="mb-4 flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-50 text-amber-700"><Gauge className="h-5 w-5" /></span>
            <div>
              <h2 className="font-semibold">Meter Estate</h2>
              <p className="text-sm text-slate-500">Assignment and connectivity</p>
            </div>
          </div>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span className="text-slate-500">Active meters</span><span className="font-semibold">{stats.active_meters || 0}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Offline meters</span><span className="font-semibold text-amber-700">{stats.offline_meters || 0}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Customers</span><span className="font-semibold">{stats.total_customers || 0}</span></div>
          </div>
        </Card>
        <Card>
          <div className="mb-4 flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-red-50 text-red-700"><AlertTriangle className="h-5 w-5" /></span>
            <div>
              <h2 className="font-semibold">Attention Queue</h2>
              <p className="text-sm text-slate-500">Issues to resolve first</p>
            </div>
          </div>
          <div className="space-y-3 text-sm">
            <div className="flex items-center justify-between"><span className="flex items-center gap-2 text-slate-500"><WalletCards className="h-4 w-4" /> Failed transactions</span><span className="font-semibold">{stats.failed_transactions || 0}</span></div>
            <div className="flex items-center justify-between"><span className="flex items-center gap-2 text-slate-500"><Activity className="h-4 w-4" /> Offline meters</span><span className="font-semibold">{stats.offline_meters || 0}</span></div>
            <div className="flex items-center justify-between"><span className="flex items-center gap-2 text-slate-500"><Users className="h-4 w-4" /> Customer records</span><span className="font-semibold">{stats.total_customers || 0}</span></div>
          </div>
        </Card>
      </div>
    </AppShell>
  )
}
