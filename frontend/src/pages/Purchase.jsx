import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { metersAPI, paymentsAPI } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'
import { useAuth } from '../context/AuthContext'

const QUICK_AMOUNTS = [100, 200, 500, 1000, 2000, 5000]

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

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setResult(null)
    try {
      const { data } = await paymentsAPI.purchase({
        meter_id: form.meter_id,
        amount: form.amount,
        phone_number: form.phone_number || undefined,
      })
      setResult(data)
      toast.success('STK Push sent! Check your phone to confirm payment.')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Purchase failed')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <LoadingSpinner />

  return (
    <div className="max-w-xl mx-auto">
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-bold text-gray-900">Buy Electricity Token</h1>
        <p className="text-gray-500">Pay via M-Pesa STK Push</p>
      </div>

      {meters.length === 0 ? (
        <div className="card text-center py-8">
          <p className="text-gray-500">Add a meter before purchasing tokens.</p>
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

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Amount (KES)</label>
            <input type="number" min="50" max="50000" className="input-field text-2xl font-bold text-center"
              value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} required />
            <div className="flex flex-wrap gap-2 mt-3">
              {QUICK_AMOUNTS.map((amt) => (
                <button key={amt} type="button"
                  onClick={() => setForm({ ...form, amount: String(amt) })}
                  className={`px-3 py-1 rounded-full text-sm border transition-colors ${
                    form.amount === String(amt) ? 'bg-primary-600 text-white border-primary-600' : 'border-gray-300 hover:border-primary-400'
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
        <div className="card mt-6 border-green-200 bg-green-50">
          <h3 className="font-semibold text-green-800 mb-2">Payment Initiated</h3>
          <p className="text-sm text-green-700">Reference: {result.reference}</p>
          <p className="text-sm text-green-700">Status: {result.status.replace(/_/g, ' ')}</p>
          <p className="text-sm text-green-600 mt-2">
            Confirm the payment on your phone. Your token will be sent via SMS and email once payment is confirmed.
          </p>
        </div>
      )}
    </div>
  )
}
