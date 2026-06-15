import { useEffect, useState } from 'react'
import { tokensAPI } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'

export default function TokenHistory() {
  const [tokens, setTokens] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    tokensAPI.history()
      .then((res) => setTokens(res.data.results || res.data))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner />

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Token History</h1>
        <p className="text-gray-500">Your generated electricity tokens</p>
      </div>

      <div className="space-y-4">
        {tokens.map((t) => (
          <div key={t.id} className="card">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm text-gray-500">Meter: {t.meter_number}</p>
                <p className="font-mono text-lg font-bold text-primary-700 mt-1 tracking-wider">{t.token}</p>
                <p className="text-sm text-gray-500 mt-1">
                  {t.token_units} kWh · KES {t.token_amount} · Ref: {t.transaction_reference}
                </p>
              </div>
              <span className={`text-xs px-2 py-1 rounded-full ${
                t.status === 'delivered' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {t.status}
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-3">
              Generated: {new Date(t.generated_at).toLocaleString()}
            </p>
          </div>
        ))}
        {tokens.length === 0 && (
          <div className="card text-center py-12">
            <p className="text-gray-500">No tokens generated yet.</p>
          </div>
        )}
      </div>
    </div>
  )
}
