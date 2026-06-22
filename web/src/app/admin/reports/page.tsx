'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AppShell } from '@/components/app-shell'
import { Card, Button, StatCard } from '@/components/ui'
import { adminApi } from '@/lib/api'

export default function AdminReportsPage() {
  const [period, setPeriod] = useState<'daily' | 'monthly'>('daily')
  const { data: analytics } = useQuery({
    queryKey: ['admin-analytics'],
    queryFn: () => adminApi.analytics().then((r) => r.data),
  })
  const { data: sales } = useQuery({
    queryKey: ['admin-sales', period],
    queryFn: () => adminApi.sales(period).then((r) => r.data),
  })

  const a = analytics || {}
  const s = sales?.data || []

  return (
    <AppShell>
      <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Admin — Reports</h1>
          <p className="text-gray-500">Sales and analytics</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant={period === 'daily' ? 'primary' : 'secondary'}
            onClick={() => setPeriod('daily')}
          >
            Daily
          </Button>
          <Button
            variant={period === 'monthly' ? 'primary' : 'secondary'}
            onClick={() => setPeriod('monthly')}
          >
            Monthly
          </Button>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        <StatCard label="Total Revenue" value={`KES ${a.total_revenue || 0}`} />
        <StatCard label="Today's Revenue" value={`KES ${a.today_revenue || 0}`} accent="text-gas-green" />
        <StatCard label="Gas Sold" value={`${a.gas_sold_units || 0} units`} />
        <StatCard label="Active Meters" value={a.active_meters || 0} />
      </div>

      <Card className="p-6">
        <h2 className="mb-4 text-lg font-semibold">
          {period.charAt(0).toUpperCase() + period.slice(1)} Sales Report
        </h2>
        {s.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No sales data yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left font-medium text-gray-500 uppercase">Date</th>
                  <th className="px-4 py-2 text-left font-medium text-gray-500 uppercase">Transactions</th>
                  <th className="px-4 py-2 text-left font-medium text-gray-500 uppercase">Revenue</th>
                  <th className="px-4 py-2 text-left font-medium text-gray-500 uppercase">Units Sold</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {s.map((row: any, i: number) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="px-4 py-3">{row.completed_at__date}</td>
                    <td className="px-4 py-3">{row.count}</td>
                    <td className="px-4 py-3 font-medium">KES {row.revenue}</td>
                    <td className="px-4 py-3">{row.units || 0} units</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </AppShell>
  )
}
