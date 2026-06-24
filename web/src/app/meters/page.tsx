'use client'

import { useQuery } from '@tanstack/react-query'
import { AppShell } from '@/components/app-shell'
import { Card, StatCard } from '@/components/ui'
import { metersApi } from '@/lib/api'

export default function MetersPage() {
  const { data: meters, isLoading } = useQuery({
    queryKey: ['meters'],
    queryFn: () => metersApi.list().then((r) => r.data.results || r.data),
  })

  return (
    <AppShell>
      <div className="mb-8">
        <div>
          <h1 className="text-2xl font-bold">My Meters</h1>
          <p className="text-gray-500">View gas meters assigned to your account</p>
        </div>
      </div>

      {isLoading ? (
        <Card className="p-8 text-center text-gray-500">Loading meters...</Card>
      ) : meters?.length === 0 ? (
        <Card className="p-8 text-center">
          <p className="text-gray-500">No meters have been assigned to your account yet.</p>
        </Card>
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          {meters.map((meter: any) => (
            <Card key={meter.id} className="p-6">
              <div className="mb-4 flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-semibold">
                    {meter.nickname || 'Meter'}
                    {meter.is_primary && (
                      <span className="ml-2 rounded-full bg-brand-100 px-2 py-0.5 text-xs font-medium text-brand-700">
                        Primary
                      </span>
                    )}
                  </h3>
                  <p className="text-sm text-gray-500 font-mono">{meter.meter_number}</p>
                </div>
                <span className={`capitalize rounded-full px-2 py-1 text-xs font-medium ${
                  meter.status === 'active' ? 'bg-green-100 text-green-700' :
                  meter.status === 'tampered' ? 'bg-red-100 text-red-700' :
                  'bg-gray-100 text-gray-700'
                }`}>
                  {meter.status}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <StatCard label="Credit" value={`${meter.current_credit} units`} />
                <StatCard label="Balance" value={`KES ${meter.current_balance}`} />
              </div>

              <div className="mt-4 space-y-2 text-sm text-gray-600">
                {meter.location && <div className="flex justify-between">
                  <span>Location</span><span>{meter.location}</span>
                </div>}
                <div className="flex justify-between">
                  <span>Valve</span><span className="capitalize">{meter.valve_status}</span>
                </div>
                {meter.tamper_status && (
                  <p className="rounded-lg bg-red-50 p-2 text-red-700">⚠ Tamper alert detected</p>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </AppShell>
  )
}
