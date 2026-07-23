'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { CheckCircle2, CreditCard, Gauge, Loader2, RefreshCw, Ticket, WalletCards } from 'lucide-react'
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
  const queryClient = useQueryClient()
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

  const retryMutation = useMutation({
    mutationFn: (reference: string) => purchaseApi.retryToken(reference).then((r) => r.data),
    onSuccess: (data) => {
      setResult(data)
      queryClient.invalidateQueries({ queryKey: ['transaction', data.reference] })
    },
    onError: (err) => {
      setFormError(getApiErrorMessage(err, 'Could not retry token generation.'))
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
      <div className="mx-auto max-w-5xl">
        <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="eyebrow">Token purchase</p>
            <h1 className="mt-1 text-3xl font-bold tracking-tight">Buy gas credit</h1>
            <p className="mt-2 max-w-2xl text-slate-500">Pay with M-Pesa, then use the generated token on the physical meter keypad.</p>
          </div>
          <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-medium text-amber-800">
            Payment first, token second
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
          <Card className="space-y-6">
            <div className="flex items-center gap-3 border-b border-slate-100 pb-4 dark:border-slate-800">
              <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal-50 text-teal-700"><WalletCards className="h-5 w-5" /></span>
              <div>
                <h2 className="font-semibold">Purchase details</h2>
                <p className="text-sm text-slate-500">Choose an assigned meter and amount</p>
              </div>
            </div>
            <div>
            <label className="mb-1 block text-sm font-semibold text-slate-700 dark:text-slate-200">Select meter</label>
            <select className="input" value={meterId} onChange={(e) => setMeterId(e.target.value)}>
              {!meters?.length && <option value="">No meters available</option>}
              {meters?.map((m: { id: string; meter_number: string; nickname: string }) => (
                <option key={m.id} value={m.id}>{m.nickname || m.meter_number} ({m.meter_number})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-semibold text-slate-700 dark:text-slate-200">Amount (KES)</label>
            <Input type="number" className="text-center text-2xl font-bold" value={amount} onChange={(e) => setAmount(e.target.value)} />
            <div className="mt-3 grid grid-cols-3 gap-2 sm:grid-cols-6">
              {QUICK.map((a) => (
                <button key={a} type="button" onClick={() => setAmount(String(a))}
                  className={`rounded-lg border px-3 py-2 text-sm font-semibold ${amount === String(a) ? 'border-teal-700 bg-teal-700 text-white' : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50'}`}>
                  KES {a}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="mb-1 block text-sm font-semibold text-slate-700 dark:text-slate-200">M-Pesa phone</label>
            <Input type="tel" placeholder="2547..." value={phone} onChange={(e) => setPhone(e.target.value)} />
          </div>
          {formError && <p className="text-sm text-red-600">{formError}</p>}
          <div className="grid gap-3 sm:grid-cols-2">
            <Button type="button" variant="secondary" className="flex-1" disabled={!canSubmit || previewMutation.isPending}
              onClick={() => previewMutation.mutate()}>
              {previewMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Gauge className="h-4 w-4" />}
              Preview Units
            </Button>
            <Button type="button" className="flex-1" disabled={!canSubmit || purchaseMutation.isPending}
              onClick={() => purchaseMutation.mutate()}>
              {purchaseMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <CreditCard className="h-4 w-4" />}
              Pay via M-Pesa
            </Button>
          </div>
        </Card>

          <div className="space-y-4">
            {preview ? (
              <div className="grid gap-3">
                <StatCard label="Expected Units" value={preview.expected_units} accent="text-teal-700" />
                <StatCard label="Gas Credit" value={preview.expected_credit} />
                <StatCard label="Total Charge" value={`KES ${preview.total}`} helper="Includes configured fees" />
              </div>
            ) : (
              <Card>
                <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 text-slate-600">
                  <Gauge className="h-5 w-5" />
                </div>
                <h3 className="font-semibold">Preview before payment</h3>
                <p className="mt-2 text-sm text-slate-500">Preview checks the vending server when available and estimates units before the STK push.</p>
              </Card>
            )}

        {transaction && (
          <Card className={`${transaction.status === 'failed' ? 'border-red-200 bg-red-50' : 'border-teal-200 bg-teal-50'}`}>
            {transaction.status === 'completed' && transaction.token ? (
              <>
                <div className="mb-3 flex items-center gap-2 font-semibold text-teal-900"><CheckCircle2 className="h-5 w-5" /> Token generated</div>
                <p className="text-sm text-teal-800">Enter this token on meter {transaction.meter_number}</p>
                <p className="mt-3 rounded-lg border border-teal-100 bg-white px-3 py-3 font-mono text-lg font-bold tracking-wide text-teal-950">
                  {transaction.token.token}
                </p>
                <p className="mt-2 text-sm text-teal-800">
                  {transaction.token.units} units · Ref: {transaction.reference}
                </p>
              </>
            ) : transaction.status === 'failed' ? (
              <>
                <h3 className="font-semibold text-red-800">Transaction needs attention</h3>
                <p className="mt-1 text-sm text-red-700">{transaction.failure_reason || 'The transaction could not be completed.'}</p>
                {transaction.failure_reason?.toLowerCase().includes('vending failed') && (
                  <Button type="button" variant="secondary" className="mt-4" disabled={retryMutation.isPending} onClick={() => retryMutation.mutate(transaction.reference)}>
                    {retryMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                    Retry Token
                  </Button>
                )}
              </>
            ) : transaction.status === 'payment_confirmed' || transaction.status === 'token_generating' ? (
              <>
                <div className="mb-2 flex items-center gap-2 font-semibold text-teal-900"><Loader2 className="h-4 w-4 animate-spin" /> Payment confirmed</div>
                <p className="text-sm text-teal-800">Generating your gas token now. Ref: {transaction.reference}</p>
              </>
            ) : (
              <>
                <div className="mb-2 flex items-center gap-2 font-semibold text-teal-900"><Ticket className="h-4 w-4" /> STK push sent</div>
                <p className="text-sm text-teal-800">Ref: {transaction.reference}. Confirm on your phone.</p>
              </>
            )}
          </Card>
        )}
          </div>
        </div>
      </div>
    </AppShell>
  )
}
