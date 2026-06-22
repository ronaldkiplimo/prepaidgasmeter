'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { AppShell } from '@/components/app-shell'
import { Card, Button, Input } from '@/components/ui'
import { authApi } from '@/lib/api'
import { useAuthStore } from '@/store/auth'

export default function ProfilePage() {
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    national_id: '',
  })
  const queryClient = useQueryClient()
  const { user, setAuth } = useAuthStore()

  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: () => authApi.profile().then((r) => {
      const data = r.data
      setFormData({
        first_name: data.first_name || '',
        last_name: data.last_name || '',
        email: data.email || '',
        national_id: data.national_id || '',
      })
      return data
    }),
  })

  const updateMutation = useMutation({
    mutationFn: (data: typeof formData) => authApi.updateProfile(data),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      // Also update the auth store with the new user data
      if (user && setAuth) {
        // Keep existing access tokens
        const access = localStorage.getItem('access_token')
        const refresh = localStorage.getItem('refresh_token')
        if (access && refresh) {
          setAuth(response.data, access, refresh)
        }
      }
      setIsEditing(false)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateMutation.mutate(formData)
  }

  return (
    <AppShell>
      <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Profile</h1>
          <p className="text-gray-500">Manage your account details</p>
        </div>
        <Button onClick={() => setIsEditing(!isEditing)}>
          {isEditing ? 'Cancel' : 'Edit Profile'}
        </Button>
      </div>

      {isLoading ? (
        <Card className="p-8 text-center text-gray-500">Loading profile...</Card>
      ) : (
        <Card className="p-6">
          {isEditing ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">First Name</label>
                  <Input
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">Last Name</label>
                  <Input
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                  />
                </div>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Email</label>
                <Input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">National ID</label>
                <Input
                  value={formData.national_id}
                  onChange={(e) => setFormData({ ...formData, national_id: e.target.value })}
                />
              </div>
              <div className="flex justify-end gap-3">
                <Button type="button" variant="secondary" onClick={() => setIsEditing(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={updateMutation.isPending}>
                  {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
                </Button>
              </div>
            </form>
          ) : (
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500">Name</p>
                <p className="font-medium">
                  {profile?.first_name} {profile?.last_name}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Phone Number</p>
                <p className="font-medium">{profile?.phone_number}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Email</p>
                <p className="font-medium">{profile?.email || 'Not set'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">National ID</p>
                <p className="font-medium">{profile?.national_id || 'Not set'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Role</p>
                <p className="font-medium capitalize">{profile?.role}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Verified</p>
                <p className="font-medium">{profile?.is_verified ? 'Yes' : 'No'}</p>
              </div>
            </div>
          )}
        </Card>
      )}
    </AppShell>
  )
}
