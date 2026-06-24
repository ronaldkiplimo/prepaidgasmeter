import { useEffect, useState } from 'react'
import { metersAPI } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Meters() {
  const [meters, setMeters] = useState([])
  const [loading, setLoading] = useState(true)

  const loadMeters = () => {
    metersAPI.list()
      .then((res) => setMeters(res.data.results || res.data))
      .finally(() => setLoading(false))
  }

  useEffect(() => { loadMeters() }, [])

  if (loading) return <LoadingSpinner />

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Meters</h1>
          <p className="text-gray-500">View gas meters assigned to your account</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {meters.map((m) => (
          <div key={m.id} className="card">
            <div className="flex justify-between items-start mb-3">
              <div>
                <h3 className="font-semibold text-lg">{m.nickname || 'Unnamed Meter'}</h3>
                <p className="text-primary-600 font-mono text-sm">{m.meter_number}</p>
              </div>
              {m.is_primary && (
                <span className="text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded">Primary</span>
              )}
            </div>
            {m.location && <p className="text-sm text-gray-500 mb-3">{m.location}</p>}
          </div>
        ))}
      </div>

      {meters.length === 0 && (
        <div className="card text-center py-12">
          <p className="text-gray-500">No meters have been assigned to your account yet.</p>
        </div>
      )}
    </div>
  )
}
