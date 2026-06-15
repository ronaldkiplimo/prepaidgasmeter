import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { metersAPI, paymentsAPI } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'

const statusColors = {
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  pending: 'bg-yellow-100 text-yellow-800',
  payment_initiated: 'bg-blue-100 text-blue-800',
  payment_confirmed: 'bg-blue-100 text-blue-800',
  token_generating: 'bg-purple-100 text-purple-800',
}

export default function Dashboard() {
  const [meters, setMeters] = useState([])
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([metersAPI.list(), paymentsAPI.transactions()])
      .then(([mRes, tRes]) => {
        setMeters(mRes.data.results || mRes.data)
        setTransactions((tRes.data.results || tRes.data).slice(0, 5))
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner />

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500">Manage your gas meters and buy prepaid gas tokens</p>
        </div>
        <Link to="/purchase" className="btn-primary">Buy Gas</Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <p className="text-sm text-gray-500">Registered Meters</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{meters.length}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Recent Transactions</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{transactions.length}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Completed</p>
          <p className="text-3xl font-bold text-green-600 mt-1">
            {transactions.filter((t) => t.status === 'completed').length}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">My Meters</h2>
            <Link to="/meters" className="text-sm text-primary-600 hover:underline">View all</Link>
          </div>
          {meters.length === 0 ? (
            <p className="text-gray-500 text-sm">No meters registered. <Link to="/meters" className="text-primary-600">Add one</Link></p>
          ) : (
            <div className="space-y-3">
              {meters.slice(0, 3).map((m) => (
                <div key={m.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium">{m.nickname || m.meter_number}</p>
                    <p className="text-sm text-gray-500">{m.meter_number}</p>
                  </div>
                  {m.is_primary && <span className="text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded">Primary</span>}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Recent Transactions</h2>
            <Link to="/transactions" className="text-sm text-primary-600 hover:underline">View all</Link>
          </div>
          {transactions.length === 0 ? (
            <p className="text-gray-500 text-sm">No transactions yet.</p>
          ) : (
            <div className="space-y-3">
              {transactions.map((t) => (
                <div key={t.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium">KES {t.amount}</p>
                    <p className="text-sm text-gray-500">{t.meter_number} · {t.reference}</p>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full ${statusColors[t.status] || 'bg-gray-100 text-gray-800'}`}>
                    {t.status.replace(/_/g, ' ')}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
