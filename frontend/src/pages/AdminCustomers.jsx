import { useEffect, useState } from 'react'
import { adminAPI } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'

export default function AdminCustomers() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    adminAPI.users()
      .then((res) => setUsers(res.data.results || res.data))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner />

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Customers</h1>
        <p className="text-gray-500">Manage platform users</p>
      </div>
      <div className="card overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500">
              <th className="py-2">Name</th>
              <th className="py-2">Phone</th>
              <th className="py-2">Role</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className="border-t border-gray-100">
                <td className="py-2">{user.first_name || user.username} {user.last_name || ''}</td>
                <td className="py-2">{user.phone_number}</td>
                <td className="py-2 capitalize">{user.role}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
