import { useEffect, useState } from 'react'
import { paymentsAPI } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'

const statusColors = {
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  pending: 'bg-yellow-100 text-yellow-800',
  payment_initiated: 'bg-blue-100 text-blue-800',
  payment_confirmed: 'bg-blue-100 text-blue-800',
  token_generating: 'bg-purple-100 text-purple-800',
}

export default function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    paymentsAPI.transactions()
      .then((res) => setTransactions(res.data.results || res.data))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner />

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Transactions</h1>
        <p className="text-gray-500">Your payment and token purchase history</p>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4 font-medium text-gray-500">Reference</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500">Meter</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500">Amount</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
              <th className="text-left py-3 px-4 font-medium text-gray-500">Date</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((t) => (
              <tr key={t.id} className="border-b border-gray-50 hover:bg-gray-50">
                <td className="py-3 px-4 font-mono text-xs">{t.reference}</td>
                <td className="py-3 px-4">{t.meter_number}</td>
                <td className="py-3 px-4 font-medium">KES {t.amount}</td>
                <td className="py-3 px-4">
                  <span className={`text-xs px-2 py-1 rounded-full ${statusColors[t.status] || 'bg-gray-100'}`}>
                    {t.status.replace(/_/g, ' ')}
                  </span>
                </td>
                <td className="py-3 px-4 text-gray-500">
                  {new Date(t.created_at).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {transactions.length === 0 && (
          <p className="text-center text-gray-500 py-8">No transactions yet.</p>
        )}
      </div>
    </div>
  )
}
