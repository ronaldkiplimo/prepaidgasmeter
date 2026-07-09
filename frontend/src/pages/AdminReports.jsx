import { useEffect, useState } from 'react'
import { adminAPI } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'

export default function AdminReports() {
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    adminAPI.dashboard()
      .then((res) => setReport(res.data))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner />

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
        <p className="text-gray-500">Platform insights</p>
      </div>
      <div className="card">
        <p className="text-sm text-gray-500">Reports are currently shown via the dashboard summary.</p>
        <pre className="mt-4 overflow-x-auto text-xs">{JSON.stringify(report, null, 2)}</pre>
      </div>
    </div>
  )
}
