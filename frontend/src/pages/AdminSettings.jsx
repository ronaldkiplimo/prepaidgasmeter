import { useEffect, useState } from 'react'
import { adminAPI } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'

export default function AdminSettings() {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    adminAPI.dashboard()
      .then((res) => setStatus(res.data))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner />

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-500">Integration and platform status</p>
      </div>
      <div className="card">
        <pre className="overflow-x-auto text-xs">{JSON.stringify(status, null, 2)}</pre>
      </div>
    </div>
  )
}
