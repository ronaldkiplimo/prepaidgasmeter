'use client'

import { useQuery } from '@tanstack/react-query'
import { AppShell } from '@/components/app-shell'
import { Card } from '@/components/ui'
import { adminApi } from '@/lib/api'

export default function AdminMetersPage() {
  const { data: meters, isLoading } = useQuery({
    queryKey: ['admin-meters'],
    queryFn: () => adminApi.meters().then((r) => r.data.results || r.data),
  })

  return (
    <AppShell>
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Admin — Meters</h1>
        <p className="text-gray-500">Manage all gas meters</p>
      </div>

      {isLoading ? (
        <Card className="p-8 text-center text-gray-500">Loading meters...</Card>
      ) : meters?.length === 0 ? (
        <Card className="p-8 text-center">
          <p className="text-gray-500">No meters registered yet.</p>
        </Card>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {meters.map((meter: any) => (
            <Card key={meter.id} className="p-6">
              <div className="mb-3 flex items-start justify-between">
                <div>
                  <h3 className="font-semibold">{meter.nickname || 'Unnamed Meter'}</h3>
                  <p className="text-sm font-mono text-gray-500">{meter.meter_number}</p>
                </div>
                <span className={`capitalize px-2 py-1 rounded text-xs font-medium ${
                  meter.status === 'active' ? 'bg-green-100 text-green-700' :
                  meter.status === 'tampered' ? 'bg-red-100 text-red-700' :
                  meter.status === 'offline' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-gray-100 text-gray-700'
                }`}>
                  {meter.status}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="text-gray-500">Credit</span>
                  <p className="font-medium">{meter.current_credit} units</p>
                </div>
                <div>
                  <span className="text-gray-500">Balance</span>
                  <p className="font-medium">KES {meter.current_balance}</p>
                </div>
                <div>
                  <span className="text-gray-500">Valve</span>
                  <p className="font-medium capitalize">{meter.valve_status}</p>
                </div>
                <div>
                  <span className="text-gray-500">Type</span>
                  <p className="font-medium capitalize">{meter.meter_type}</p>
                </div>
              </div>
              {meter.tamper_status && (
                <div className="mt-3 rounded bg-red-50 px-3 py-2 text-sm text-red-700">
                  ⚠️ Tamper alert detected
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </AppShell>
  )
}
