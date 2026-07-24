import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { metersAPI, paymentsAPI } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'
import { useAuth } from '../context/AuthContext'

const QUICK_AMOUNTS = [100, 200, 500, 1000, 2000, 5000]

function formatApiError(data) {
  if (!data) return 'Purchase failed'
  if (typeof data === 'string') return data
  if (data.detail) return data.detail

  return Object.entries(data)
    .map(([field, value]) => {
      const message = Array.isArray(value) ? value.join(', ') : String(value)
      return `${field.replace(/_/g, ' ')}: ${message}`
    })
    .join('\n') || 'Purchase failed'
}

export default function Purchase() {
  const { user } = useAuth()
  const [meters, setMeters] = useState([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState(null)
  const [form, setForm] = useState({
    meter_id: '', amount: '', phone_number: user?.phone_number || '',
  })

  useEffect(() => {
    metersAPI.list()
      .then((res) => {
        const data = res.data.results || res.data
        setMeters(data)
        const primary = data.find((m) => m.is_primary) || data[0]
        if (primary) setForm((f) => ({ ...f, meter_id: primary.id }))
      })
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!result?.reference || ['completed', 'failed', 'refunded'].includes(result.status)) return

    const poll = window.setInterval(async () => {
      try {
        const { data } = await paymentsAPI.transaction(result.reference)
        setResult(data)
      } catch {
        // Keep polling; transient network errors should not hide payment progress.
      }
    }, 3000)

    return () => window.clearInterval(poll)
  }, [result?.reference, result?.status])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setResult(null)
    try {
      const { data } = await paymentsAPI.purchase({
        meter_id: form.meter_id,
        amount: Number(form.amount),
        phone_number: form.phone_number.trim() || undefined,
      })
      setResult(data)
      toast.success('STK Push sent! Check your phone to confirm payment.')
    } catch (err) {
      toast.error(formatApiError(err.response?.data))
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <LoadingSpinner />

  return (
    <div className="max-w-xl mx-auto">
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-bold text-gray-900">Buy Gas Token</h1>
        <p className="text-gray-500">Pay via M-Pesa STK Push</p>
      </div>

      {meters.length === 0 ? (
        <div className="card text-center py-8">
          <p className="text-gray-500">Add a gas meter before purchasing tokens.</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="card space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Select Meter</label>
            <select className="input-field" value={form.meter_id}
              onChange={(e) => setForm({ ...form, meter_id: e.target.value })} required>
              {meters.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.nickname || m.meter_number} ({m.meter_number})
                </option>
              ))}
            </select>
          </div>

          <div className="bg-gradient-to-r from-primary-50 to-amber-50 rounded-xl p-5 border-2 border-primary-200">
            <div className="flex items-center gap-2 mb-3">
              <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 text-primary-700">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">

                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.51-1.31c-.562-.649-1.413-1.076-2.353-1.253V5z" clipRule="evenodd" />
                </svg>
              </span>
              <label className="text-lg font-bold text-gray-800">Amount (KES)</label>
            </div>
            <input type="number" min="50" max="50000" className="input-field text-3xl font-extrabold text-center border-primary-300 bg-white shadow-inner"
              value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} required />
            <div className="flex flex-wrap gap-2 mt-3">
              {QUICK_AMOUNTS.map((amt) => (
                <button key={amt} type="button"
                  onClick={() => setForm({ ...form, amount: String(amt) })}
                  className={`px-4 py-1.5 rounded-full text-sm font-semibold border-2 transition-all ${
                    form.amount === String(amt) ? 'bg-primary-600 text-white border-primary-600 shadow-md scale-105' : 'border-primary-200 bg-primary-50 text-primary-700 hover:bg-primary-100 hover:border-primary-300'
                  }`}>
                  KES {amt}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">M-Pesa Phone Number</label>
            <input type="tel" className="input-field" placeholder="254712345678"
              value={form.phone_number} onChange={(e) => setForm({ ...form, phone_number: e.target.value })} />
          </div>

          <button type="submit" className="btn-primary w-full py-3 text-lg" disabled={submitting}>
            {submitting ? 'Processing...' : `Pay KES ${form.amount || '0'} via M-Pesa`}
          </button>
        </form>
      )}

      {result && (
        <div className={`card mt-6 ${result.status === 'failed' ? 'border-red-200 bg-red-50' : 'border-green-200 bg-green-50'}`}>
          {result.status === 'completed' && result.token ? (
            <>
              <h3 className="font-semibold text-green-800 mb-2">Payment Successful</h3>
              <p className="text-sm text-green-700">Token generated for {result.meter_number}</p>
              <p className="font-mono text-lg font-bold text-green-900 bg-white rounded-md px-3 py-2 mt-3">{result.token.token}</p>
              <p className="text-sm text-green-700 mt-2">{result.token.units} units · Ref: {result.reference}</p>
            </>
          ) : result.status === 'failed' ? (
            <>
              <h3 className="font-semibold text-red-800 mb-2">Payment Failed</h3>
              <p className="text-sm text-red-700">{result.failure_reason || 'The transaction could not be completed.'}</p>
            </>
          ) : result.status === 'payment_confirmed' || result.status === 'token_generating' ? (
            <>
              <h3 className="font-semibold text-green-800 mb-2">Payment Confirmed</h3>
              <p className="text-sm text-green-700">Generating your gas token now. Ref: {result.reference}</p>
            </>
          ) : (
            <>
              <h3 className="font-semibold text-green-800 mb-2">Payment Initiated</h3>
              <p className="text-sm text-green-700">Reference: {result.reference}</p>
              <p className="text-sm text-green-700">Status: {result.status.replace(/_/g, ' ')}</p>
              <p className="text-sm text-green-600 mt-2">
                Confirm the payment on your phone. Your gas token will be shown here once payment is confirmed.
              </p>
            </>
          )}
        </div>
      )}
    </div>
  )
}
