import { useEffect, useState } from 'react'
import { adminAPI } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'

export default function AdminTransactions() {
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    adminAPI.transactions()
      .then((res) => setTransactions(res.data.results || res.data))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner />

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Transactions</h1>
        <p className="text-gray-500">All gas purchase transactions</p>
      </div>
      <div className="space-y-3">
        {transactions.map((txn) => (
          <div key={txn.id} className="card flex justify-between">
            <div>
              <p className="font-medium">{txn.reference}</p>
              <p className="text-sm text-gray-500">{txn.meter_number || 'N/A'}</p>
            </div>
            <div className="text-right">
              <p className="font-medium">KES {txn.amount}</p>
              <p className="text-sm text-gray-500 capitalize">{txn.status}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
