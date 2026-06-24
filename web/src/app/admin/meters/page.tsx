'use client'

import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { AppShell } from '@/components/app-shell'
import { Button, Card, Input } from '@/components/ui'
import { adminApi, metersApi } from '@/lib/api'

export default function AdminMetersPage() {
  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState({ user: '', meter_number: '', nickname: '', location: '' })
  const [assignments, setAssignments] = useState<Record<string, string>>({})
  const queryClient = useQueryClient()

  const { data: meters, isLoading } = useQuery({
    queryKey: ['admin-meters'],
    queryFn: () => adminApi.meters().then((r) => r.data.results || r.data),
  })

  const { data: users } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => adminApi.users().then((r) => r.data.results || r.data),
  })

  const addMutation = useMutation({
    mutationFn: (data: typeof form) => metersApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-meters'] })
      queryClient.invalidateQueries({ queryKey: ['meters'] })
      setShowAdd(false)
      setForm({ user: '', meter_number: '', nickname: '', location: '' })
    },
  })

  const reassignMutation = useMutation({
    mutationFn: ({ meterId, userId }: { meterId: string; userId: string }) =>
      metersApi.update(meterId, { user: userId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-meters'] })
      queryClient.invalidateQueries({ queryKey: ['meters'] })
    },
  })

  return (
    <AppShell>
      <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Admin — Meters</h1>
          <p className="text-gray-500">Create meters and assign them to users</p>
        </div>
        <Button onClick={() => setShowAdd(!showAdd)}>
          {showAdd ? 'Cancel' : 'Add Meter'}
        </Button>
      </div>

      {showAdd && (
        <Card className="mb-8 p-6">
          <h2 className="mb-4 text-lg font-semibold">Register New Meter</h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Assign To</label>
              <select
                className="input"
                value={form.user}
                onChange={(e) => setForm({ ...form, user: e.target.value })}
              >
                <option value="">Select user</option>
                {users?.map((user: any) => (
                  <option key={user.id} value={user.id}>
                    {user.first_name || user.username || user.phone_number} ({user.phone_number})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Meter Number</label>
              <Input
                placeholder="e.g. STRON123456"
                value={form.meter_number}
                onChange={(e) => setForm({ ...form, meter_number: e.target.value })}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Nickname</label>
              <Input
                placeholder="Kitchen Meter"
                value={form.nickname}
                onChange={(e) => setForm({ ...form, nickname: e.target.value })}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Location</label>
              <Input
                placeholder="Nairobi, Kenya"
                value={form.location}
                onChange={(e) => setForm({ ...form, location: e.target.value })}
              />
            </div>
          </div>
          {addMutation.isError && (
            <p className="mt-3 text-sm text-red-600">Could not add meter. Check the selected user and meter number.</p>
          )}
          <div className="mt-4 flex justify-end">
            <Button
              onClick={() => addMutation.mutate(form)}
              disabled={addMutation.isPending || !form.user || !form.meter_number}
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
                  <p className="text-sm text-gray-500">
                    {meter.user_display_name || 'Assigned user'} · {meter.user_phone_number || meter.user}
                  </p>
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
              <div className="mt-4 flex flex-col gap-2 border-t border-gray-100 pt-4 sm:flex-row">
                <select
                  className="input"
                  value={assignments[meter.id] ?? meter.user ?? ''}
                  onChange={(e) => setAssignments({ ...assignments, [meter.id]: e.target.value })}
                >
                  {users?.map((user: any) => (
                    <option key={user.id} value={user.id}>
                      {user.first_name || user.username || user.phone_number} ({user.phone_number})
                    </option>
                  ))}
                </select>
                <Button
                  variant="secondary"
                  onClick={() => reassignMutation.mutate({ meterId: meter.id, userId: assignments[meter.id] ?? meter.user })}
                  disabled={reassignMutation.isPending || (assignments[meter.id] ?? meter.user) === meter.user}
                  className="shrink-0"
                >
                  Save Assignment
                </Button>
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
