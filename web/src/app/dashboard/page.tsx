'use client'

import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { AlertTriangle, ArrowRight, Gauge, Ticket, WalletCards } from 'lucide-react'
import { AppShell } from '@/components/app-shell'
import { StatCard, Card, Button } from '@/components/ui'
import { metersApi, purchaseApi } from '@/lib/api'

export default function DashboardPage() {
  const { data: meters } = useQuery({ queryKey: ['meters'], queryFn: () => metersApi.list().then((r) => r.data.results || r.data) })
  const { data: txns } = useQuery({ queryKey: ['transactions'], queryFn: () => purchaseApi.transactions().then((r) => r.data.results || r.data) })

  const primary = meters?.find((m: { is_primary: boolean }) => m.is_primary) || meters?.[0]
  const completed = (txns || []).filter((t: { status: string }) => t.status === 'completed').length
  const inProgress = (txns || []).filter((t: { status: string }) => ['payment_initiated', 'payment_confirmed', 'token_generating'].includes(t.status)).length

  return (
    <AppShell>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="eyebrow">Customer workspace</p>
          <h1 className="mt-1 text-3xl font-bold tracking-tight">Gas credit and meter status</h1>
          <p className="mt-2 max-w-2xl text-slate-500">Buy credit, receive a Stron token, and enter it on your assigned meter to open or top up gas supply.</p>
        </div>
        <Link href="/buy-gas"><Button><WalletCards className="h-4 w-4" /> Buy Gas Credit</Button></Link>
      </div>

      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Current Credit" value={primary ? `${primary.current_credit} units` : 'Awaiting meter'} accent="text-teal-700" helper={primary?.meter_number} />
        <StatCard label="Meter Balance" value={primary ? `KES ${primary.current_balance}` : '-'} />
        <StatCard label="Assigned Meters" value={meters?.length ?? 0} helper="Admin managed" />
        <StatCard label="Completed Tokens" value={completed} helper={inProgress ? `${inProgress} in progress` : 'All clear'} />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <Card className="overflow-hidden p-0">
          <div className="border-b border-slate-100 p-5 dark:border-slate-800">
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal-50 text-teal-700"><Gauge className="h-5 w-5" /></span>
              <div>
                <h2 className="font-semibold">Primary Meter</h2>
                <p className="text-sm text-slate-500">Live account record</p>
              </div>
            </div>
          </div>
          {!primary ? (
            <div className="p-5 text-slate-500">No meters have been assigned to your account yet.</div>
          ) : (
            <div className="grid gap-0 text-sm">
              {[
                ['Meter number', primary.meter_number],
                ['Status', primary.status],
                ['Valve', primary.valve_status],
                ['Current credit', `${primary.current_credit} units`],
              ].map(([label, value]) => (
                <div key={label} className="flex items-center justify-between border-b border-slate-100 px-5 py-3 last:border-0 dark:border-slate-800">
                  <span className="text-slate-500">{label}</span>
                  <span className="font-semibold capitalize text-slate-900 dark:text-white">{value}</span>
                </div>
              ))}
              {primary.tamper_status && (
                <div className="m-5 flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 p-3 text-sm font-medium text-red-700">
                  <AlertTriangle className="h-4 w-4" /> Tamper alert detected
                </div>
              )}
            </div>
          )}
        </Card>
        <Card>
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="font-semibold">Recent Purchases</h2>
              <p className="text-sm text-slate-500">Latest token activity</p>
            </div>
            <Ticket className="h-5 w-5 text-amber-600" />
          </div>
          {(txns || []).slice(0, 5).map((t: { id: string; reference: string; amount: string; status: string }) => (
            <div key={t.id} className="flex items-center justify-between border-b border-slate-100 py-3 text-sm last:border-0 dark:border-slate-800">
              <div>
                <p className="font-mono font-semibold">{t.reference}</p>
                <p className="capitalize text-slate-500">{t.status.replace('_', ' ')}</p>
              </div>
              <span className="text-lg font-bold text-teal-700 bg-teal-50 px-3 py-1 rounded-lg">KES {t.amount}</span>
            </div>
          ))}
          {!txns?.length && <p className="text-sm text-slate-500">No purchases yet.</p>}
          <Link href="/transactions" className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-teal-700">
            View all transactions <ArrowRight className="h-4 w-4" />
          </Link>
        </Card>
      </div>
    </AppShell>
  )
}
