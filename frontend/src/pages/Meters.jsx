import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { metersAPI } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Meters() {
  const [meters, setMeters] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    meter_number: '', nickname: '', account_number: '', location: '', is_primary: false,
  })

  const loadMeters = () => {
    metersAPI.list()
      .then((res) => setMeters(res.data.results || res.data))
      .finally(() => setLoading(false))
  }

  useEffect(() => { loadMeters() }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await metersAPI.create(form)
      toast.success('Meter added successfully')
      setShowForm(false)
      setForm({ meter_number: '', nickname: '', account_number: '', location: '', is_primary: false })
      loadMeters()
    } catch (err) {
      toast.error(err.response?.data?.meter_number?.[0] || 'Failed to add meter')
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Remove this meter?')) return
    try {
      await metersAPI.delete(id)
      toast.success('Meter removed')
      loadMeters()
    } catch {
      toast.error('Failed to remove meter')
    }
  }

  if (loading) return <LoadingSpinner />

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Meters</h1>
          <p className="text-gray-500">Manage your registered electricity meters</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary">
          {showForm ? 'Cancel' : 'Add Meter'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="card mb-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Meter Number *</label>
              <input className="input-field" value={form.meter_number}
                onChange={(e) => setForm({ ...form, meter_number: e.target.value })} required />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nickname</label>
              <input className="input-field" placeholder="Home, Office..."
                value={form.nickname} onChange={(e) => setForm({ ...form, nickname: e.target.value })} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Account Number</label>
              <input className="input-field" value={form.account_number}
                onChange={(e) => setForm({ ...form, account_number: e.target.value })} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
              <input className="input-field" value={form.location}
                onChange={(e) => setForm({ ...form, location: e.target.value })} />
            </div>
          </div>
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={form.is_primary}
              onChange={(e) => setForm({ ...form, is_primary: e.target.checked })} />
            <span className="text-sm text-gray-700">Set as primary meter</span>
          </label>
          <button type="submit" className="btn-primary">Save Meter</button>
        </form>
      )}

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
            <button onClick={() => handleDelete(m.id)} className="text-sm text-red-600 hover:underline">
              Remove
            </button>
          </div>
        ))}
      </div>

      {meters.length === 0 && !showForm && (
        <div className="card text-center py-12">
          <p className="text-gray-500">No meters registered yet.</p>
          <button onClick={() => setShowForm(true)} className="btn-primary mt-4">Add Your First Meter</button>
        </div>
      )}
    </div>
  )
}
