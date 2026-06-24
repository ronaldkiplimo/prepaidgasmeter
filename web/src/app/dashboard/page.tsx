'use client'

import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { AppShell } from '@/components/app-shell'
import { StatCard, Card, Button } from '@/components/ui'
import { metersApi, purchaseApi } from '@/lib/api'

export default function DashboardPage() {
  const { data: meters } = useQuery({ queryKey: ['meters'], queryFn: () => metersApi.list().then((r) => r.data.results || r.data) })
  const { data: txns } = useQuery({ queryKey: ['transactions'], queryFn: () => purchaseApi.transactions().then((r) => r.data.results || r.data) })

  const primary = meters?.find((m: { is_primary: boolean }) => m.is_primary) || meters?.[0]

  return (
    <AppShell>
      <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Customer Dashboard</h1>
          <p className="text-gray-500">Manage your gas meters and credit</p>
        </div>
        <Link href="/buy-gas"><Button>Buy Gas Credit</Button></Link>
      </div>

      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Current Credit" value={primary ? `${primary.current_credit} units` : '—'} accent="text-gas-green" />
        <StatCard label="Balance" value={primary ? `KES ${primary.current_balance}` : '—'} />
        <StatCard label="Registered Meters" value={meters?.length ?? 0} />
        <StatCard label="Recent Purchases" value={txns?.length ?? 0} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <h2 className="mb-4 text-lg font-semibold">Meter Status</h2>
          {!primary ? (
            <p className="text-gray-500">No meters have been assigned to your account yet.</p>
          ) : (
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span>Meter</span><span className="font-mono">{primary.meter_number}</span></div>
              <div className="flex justify-between"><span>Status</span><span className="capitalize">{primary.status}</span></div>
              <div className="flex justify-between"><span>Valve</span><span className="capitalize">{primary.valve_status}</span></div>
              {primary.tamper_status && <p className="rounded-lg bg-red-50 p-2 text-red-700">⚠ Tamper alert detected</p>}
            </div>
          )}
        </Card>
        <Card>
          <h2 className="mb-4 text-lg font-semibold">Recent Purchases</h2>
          {(txns || []).slice(0, 5).map((t: { id: string; reference: string; amount: string; status: string }) => (
            <div key={t.id} className="flex justify-between border-b border-gray-100 py-2 text-sm last:border-0">
              <span>{t.reference}</span>
              <span>KES {t.amount} · {t.status}</span>
            </div>
          ))}
        </Card>
      </div>
    </AppShell>
  )
}
