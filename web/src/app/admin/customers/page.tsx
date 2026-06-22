'use client'

import { useQuery } from '@tanstack/react-query'
import { AppShell } from '@/components/app-shell'
import { Card } from '@/components/ui'
import { adminApi } from '@/lib/api'

export default function AdminCustomersPage() {
  const { data: users, isLoading } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => adminApi.users().then((r) => r.data.results || r.data),
  })

  return (
    <AppShell>
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Admin — Customers & Users</h1>
        <p className="text-gray-500">Manage all platform users</p>
      </div>

      {isLoading ? (
        <Card className="p-8 text-center text-gray-500">Loading users...</Card>
      ) : users?.length === 0 ? (
        <Card className="p-8 text-center">
          <p className="text-gray-500">No users yet.</p>
        </Card>
      ) : (
        <div className="overflow-x-auto">
          <Card className="p-0">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-6 py-3 text-left font-medium text-gray-500 uppercase">Phone</th>
                  <th className="px-6 py-3 text-left font-medium text-gray-500 uppercase">Email</th>
                  <th className="px-6 py-3 text-left font-medium text-gray-500 uppercase">Role</th>
                  <th className="px-6 py-3 text-left font-medium text-gray-500 uppercase">Verified</th>
                  <th className="px-6 py-3 text-left font-medium text-gray-500 uppercase">Joined</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {users.map((user: any) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="font-medium">{user.first_name || ''} {user.last_name || ''}</div>
                      <div className="text-gray-500 text-xs">{user.username}</div>
                    </td>
                    <td className="px-6 py-4 font-mono text-gray-700">{user.phone_number}</td>
                    <td className="px-6 py-4 text-gray-600">{user.email || '-'}</td>
                    <td className="px-6 py-4">
                      <span className={`capitalize px-2 py-1 rounded text-xs font-medium ${
                        user.role === 'admin' ? 'bg-purple-100 text-purple-700' :
                        user.role === 'distributor' ? 'bg-blue-100 text-blue-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        user.is_verified ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                      }`}>
                        {user.is_verified ? 'Yes' : 'No'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-500">
                      {new Date(user.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      )}
    </AppShell>
  )
}
