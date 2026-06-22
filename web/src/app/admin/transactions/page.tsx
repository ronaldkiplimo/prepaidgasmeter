'use client'

import { useQuery } from '@tanstack/react-query'
import { AppShell } from '@/components/app-shell'
import { Card } from '@/components/ui'
import { adminApi } from '@/lib/api'

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString()
}

function getStatusColor(status: string) {
  switch (status) {
    case 'completed': return 'bg-green-100 text-green-700'
    case 'pending':
    case 'payment_initiated':
    case 'token_generating': return 'bg-yellow-100 text-yellow-700'
    case 'payment_confirmed': return 'bg-blue-100 text-blue-700'
    case 'failed':
    case 'refunded': return 'bg-red-100 text-red-700'
    default: return 'bg-gray-100 text-gray-700'
  }
}

export default function AdminTransactionsPage() {
  const { data: transactions, isLoading } = useQuery({
    queryKey: ['admin-transactions'],
    queryFn: () => adminApi.transactions().then((r) => r.data.results || r.data),
  })

  return (
    <AppShell>
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Admin — Transactions</h1>
        <p className="text-gray-500">All gas purchase transactions</p>
      </div>

      {isLoading ? (
        <Card className="p-8 text-center text-gray-500">Loading transactions...</Card>
      ) : transactions?.length === 0 ? (
        <Card className="p-8 text-center">
          <p className="text-gray-500">No transactions yet.</p>
        </Card>
      ) : (
        <div className="space-y-4">
          {transactions.map((txn: any) => (
            <Card key={txn.id} className="p-6">
              <div className="flex flex-wrap items-start justify-between gap-4 mb-4">
                <div>
                  <div className="flex items-center gap-3">
                    <h3 className="font-semibold font-mono">{txn.reference}</h3>
                    <span className={`capitalize px-2 py-1 rounded text-xs font-medium ${getStatusColor(txn.status)}`}>
                      {txn.status.replace('_', ' ')}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 mt-1">
                    {txn.user?.phone_number || 'N/A'} • {txn.meter_number} • {formatDate(txn.created_at)}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold">KES {txn.amount}</p>
                  {txn.token && (
                    <p className="text-sm text-green-600">{txn.token.token_units} units</p>
                  )}
                </div>
              </div>

              <div className="grid gap-3 md:grid-cols-3 text-sm">
                {txn.mpesa_receipt && (
                  <div className="rounded bg-gray-50 p-3">
                    <span className="text-gray-500">M-Pesa Receipt</span>
                    <p className="font-mono font-medium">{txn.mpesa_receipt}</p>
                  </div>
                )}
                {txn.token && (
                  <div className="rounded bg-green-50 p-3">
                    <span className="text-green-600">Token</span>
                    <p className="font-mono font-medium">{txn.token.token}</p>
                  </div>
                )}
                {txn.expected_units && (
                  <div className="rounded bg-blue-50 p-3">
                    <span className="text-blue-600">Expected Units</span>
                    <p className="font-medium">{txn.expected_units}</p>
                  </div>
                )}
              </div>

              {txn.failure_reason && (
                <div className="mt-4 rounded bg-red-50 p-3 text-sm text-red-700">
                  {txn.failure_reason}
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </AppShell>
  )
}
