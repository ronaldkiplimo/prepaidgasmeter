'use client'

import { useQuery, useMutation } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { AppShell } from '@/components/app-shell'
import { Button, Card, Input, StatCard } from '@/components/ui'
import { metersApi, purchaseApi } from '@/lib/api'
import { useAuthStore } from '@/store/auth'

const QUICK = [100, 200, 500, 1000, 2000, 5000]

export default function BuyGasPage() {
  const user = useAuthStore((s) => s.user)
  const { data: meters } = useQuery({ queryKey: ['meters'], queryFn: () => metersApi.list().then((r) => r.data.results || r.data) })
  const [meterId, setMeterId] = useState('')
  const [amount, setAmount] = useState('')
  const [phone, setPhone] = useState(user?.phone_number || '')
  const [preview, setPreview] = useState<Record<string, string> | null>(null)
  const [result, setResult] = useState<Record<string, string> | null>(null)

  const previewMutation = useMutation({
    mutationFn: () => purchaseApi.preview({ meter_id: meterId, amount: Number(amount) }).then((r) => r.data),
    onSuccess: setPreview,
  })

  const purchaseMutation = useMutation({
    mutationFn: () => purchaseApi.purchase({ meter_id: meterId, amount: Number(amount), phone_number: phone }).then((r) => r.data),
    onSuccess: setResult,
  })

  useEffect(() => {
    if (meters?.length && !meterId) {
      const primary = meters.find((m: { is_primary: boolean }) => m.is_primary) || meters[0]
      setMeterId(primary.id)
    }
  }, [meters, meterId])

  return (
    <AppShell>
      <div className="mx-auto max-w-xl">
        <h1 className="mb-2 text-2xl font-bold">Buy Gas Credit</h1>
        <p className="mb-8 text-gray-500">Pay securely via M-Pesa STK Push</p>

        <Card className="space-y-6">
          <div>
            <label className="mb-1 block text-sm font-medium">Select Meter</label>
            <select className="input" value={meterId} onChange={(e) => setMeterId(e.target.value)}>
              {meters?.map((m: { id: string; meter_number: string; nickname: string }) => (
                <option key={m.id} value={m.id}>{m.nickname || m.meter_number} ({m.meter_number})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Amount (KES)</label>
            <Input type="number" className="text-center text-2xl font-bold" value={amount} onChange={(e) => setAmount(e.target.value)} />
            <div className="mt-3 flex flex-wrap gap-2">
              {QUICK.map((a) => (
                <button key={a} type="button" onClick={() => setAmount(String(a))}
                  className={`rounded-full border px-3 py-1 text-sm ${amount === String(a) ? 'border-brand-600 bg-brand-600 text-white' : 'border-gray-300'}`}>
                  KES {a}
                </button>
              ))}
            </div>
          </div>
          <Input type="tel" placeholder="M-Pesa phone" value={phone} onChange={(e) => setPhone(e.target.value)} />
          <div className="flex gap-3">
            <Button type="button" variant="secondary" className="flex-1" disabled={!amount || previewMutation.isPending}
              onClick={() => previewMutation.mutate()}>Preview Units</Button>
            <Button type="button" className="flex-1" disabled={!amount || purchaseMutation.isPending}
              onClick={() => purchaseMutation.mutate()}>Pay via M-Pesa</Button>
          </div>
        </Card>

        {preview && (
          <Card className="mt-6 grid gap-3 sm:grid-cols-3">
            <StatCard label="Expected Units" value={preview.expected_units} accent="text-gas-green" />
            <StatCard label="Expected Credit" value={preview.expected_credit} />
            <StatCard label="Total" value={`KES ${preview.total}`} />
          </Card>
        )}

        {result && (
          <Card className="mt-6 border-green-200 bg-green-50">
            <h3 className="font-semibold text-green-800">STK Push Sent</h3>
            <p className="text-sm text-green-700">Ref: {result.reference} · Confirm on your phone</p>
          </Card>
        )}
      </div>
    </AppShell>
  )
}
