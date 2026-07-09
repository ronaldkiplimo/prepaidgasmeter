'use client'

import { useMutation, useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { AppShell } from '@/components/app-shell'
import { Button, Card, Input, StatCard } from '@/components/ui'
import { getApiErrorMessage, metersApi, purchaseApi } from '@/lib/api'
import { useAuthStore } from '@/store/auth'

const QUICK = [100, 200, 500, 1000, 2000, 5000]

type PurchaseTransaction = {
  reference: string
  status: string
  meter_number?: string
  failure_reason?: string
  token?: {
    token: string
    units?: string
    status?: string
  } | null
}

export default function BuyGasPage() {
  const user = useAuthStore((s) => s.user)
  const { data: meters } = useQuery({ queryKey: ['meters'], queryFn: () => metersApi.list().then((r) => r.data.results || r.data) })
  const [meterId, setMeterId] = useState('')
  const [amount, setAmount] = useState('')
  const [phone, setPhone] = useState(user?.phone_number || '')
  const [preview, setPreview] = useState<Record<string, string> | null>(null)
  const [result, setResult] = useState<PurchaseTransaction | null>(null)
  const [formError, setFormError] = useState('')
  const activeReference = result?.reference
  const canSubmit = Boolean(meterId && amount && Number(amount) > 0)

  const transactionQuery = useQuery<PurchaseTransaction>({
    queryKey: ['transaction', activeReference],
    queryFn: () => purchaseApi.transaction(activeReference as string).then((r) => r.data),
    enabled: Boolean(activeReference),
    refetchInterval: (query) => {
      const status = query.state.data?.status
      return status && ['completed', 'failed', 'refunded'].includes(status) ? false : 3000
    },
  })

  const transaction = transactionQuery.data || result

  const previewMutation = useMutation({
    mutationFn: () => purchaseApi.preview({ meter_id: meterId, amount: Number(amount) }).then((r) => r.data),
    onMutate: () => {
      setFormError('')
      setResult(null)
    },
    onSuccess: setPreview,
    onError: (err) => {
      setFormError(getApiErrorMessage(err, 'Could not preview this purchase.'))
    },
  })

  const purchaseMutation = useMutation({
    mutationFn: () => purchaseApi.purchase({ meter_id: meterId, amount: Number(amount), phone_number: phone }).then((r) => r.data),
    onMutate: () => {
      setFormError('')
      setResult(null)
    },
    onSuccess: setResult,
    onError: (err) => {
      setFormError(getApiErrorMessage(err, 'Could not start the M-Pesa payment.'))
    },
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
              {!meters?.length && <option value="">No meters available</option>}
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
          {formError && <p className="text-sm text-red-600">{formError}</p>}
          <div className="flex gap-3">
            <Button type="button" variant="secondary" className="flex-1" disabled={!canSubmit || previewMutation.isPending}
              onClick={() => previewMutation.mutate()}>Preview Units</Button>
            <Button type="button" className="flex-1" disabled={!canSubmit || purchaseMutation.isPending}
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

        {transaction && (
          <Card className={`mt-6 ${transaction.status === 'failed' ? 'border-red-200 bg-red-50' : 'border-green-200 bg-green-50'}`}>
            {transaction.status === 'completed' && transaction.token ? (
              <>
                <h3 className="font-semibold text-green-800">Payment Successful</h3>
                <p className="text-sm text-green-700">Token generated for {transaction.meter_number}</p>
                <p className="mt-3 rounded-md bg-white px-3 py-2 font-mono text-lg font-bold text-green-900">
                  {transaction.token.token}
                </p>
                <p className="mt-2 text-sm text-green-700">
                  {transaction.token.units} units · Ref: {transaction.reference}
                </p>
              </>
            ) : transaction.status === 'failed' ? (
              <>
                <h3 className="font-semibold text-red-800">Payment Failed</h3>
                <p className="text-sm text-red-700">{transaction.failure_reason || 'The transaction could not be completed.'}</p>
              </>
            ) : transaction.status === 'payment_confirmed' || transaction.status === 'token_generating' ? (
              <>
                <h3 className="font-semibold text-green-800">Payment Confirmed</h3>
                <p className="text-sm text-green-700">Generating your gas token now. Ref: {transaction.reference}</p>
              </>
            ) : (
              <>
                <h3 className="font-semibold text-green-800">STK Push Sent</h3>
                <p className="text-sm text-green-700">Ref: {transaction.reference} · Confirm on your phone</p>
              </>
            )}
          </Card>
        )}
      </div>
    </AppShell>
  )
}
