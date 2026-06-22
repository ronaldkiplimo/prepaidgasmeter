'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { AppShell } from '@/components/app-shell'
import { Card, Button, Input, StatCard } from '@/components/ui'
import { metersApi } from '@/lib/api'

export default function MetersPage() {
  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState({ meter_number: '', nickname: '', location: '' })
  const queryClient = useQueryClient()

  const { data: meters, isLoading } = useQuery({
    queryKey: ['meters'],
    queryFn: () => metersApi.list().then((r) => r.data.results || r.data),
  })

  const addMutation = useMutation({
    mutationFn: (data: typeof form) => metersApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meters'] })
      setShowAdd(false)
      setForm({ meter_number: '', nickname: '', location: '' })
    },
  })

  return (
    <AppShell>
      <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">My Meters</h1>
          <p className="text-gray-500">Manage your registered gas meters</p>
        </div>
        <Button onClick={() => setShowAdd(!showAdd)}>
          {showAdd ? 'Cancel' : 'Add Meter'}
        </Button>
      </div>

      {showAdd && (
        <Card className="mb-8 p-6">
          <h2 className="mb-4 text-lg font-semibold">Register New Meter</h2>
          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Meter Number</label>
              <Input
                placeholder="e.g. STRON123456"
                value={form.meter_number}
                onChange={(e) => setForm({ ...form, meter_number: e.target.value })}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Nickname (optional)</label>
              <Input
                placeholder="Kitchen Meter"
                value={form.nickname}
                onChange={(e) => setForm({ ...form, nickname: e.target.value })}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Location (optional)</label>
              <Input
                placeholder="Nairobi, Kenya"
                value={form.location}
                onChange={(e) => setForm({ ...form, location: e.target.value })}
              />
            </div>
          </div>
          <div className="mt-4 flex justify-end">
            <Button
              onClick={() => addMutation.mutate(form)}
              disabled={addMutation.isPending || !form.meter_number}
            >
              {addMutation.isPending ? 'Adding...' : 'Register Meter'}
            </Button>
          </div>
        </Card>
      )}

      {isLoading ? (
        <Card className="p-8 text-center text-gray-500">Loading meters...</Card>
      ) : meters?.length === 0 ? (
        <Card className="p-8 text-center">
          <p className="text-gray-500">No meters registered yet. Add your first meter above!</p>
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
