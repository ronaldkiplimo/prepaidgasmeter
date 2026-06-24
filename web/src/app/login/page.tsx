'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { authApi } from '@/lib/api'
import { useAuthStore } from '@/store/auth'
import { Button, Card, Input } from '@/components/ui'

export default function LoginPage() {
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { setAuth } = useAuthStore()
  const router = useRouter()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { data } = await authApi.login(phone, password)
      setAuth(data.user, data.access, data.refresh)
      router.push(data.user.role === 'admin' ? '/admin' : '/dashboard')
    } catch {
      setError('Invalid phone number or password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-brand-700 to-brand-900 px-4">
      <Card className="w-full max-w-md p-8 shadow-md">
        <div className="mb-8 text-center">
          <div className="flex items-center justify-center gap-3">
            <div className="w-12 h-12 rounded-full bg-brand-600 text-white flex items-center justify-center text-lg font-bold">PG</div>
            <h1 className="text-2xl font-bold text-gray-900">PrepaidGas Kenya</h1>
          </div>
          <p className="mt-2 text-gray-500">Buy gas credit instantly via M-Pesa</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Phone Number</label>
            <Input type="tel" placeholder="254712345678" value={phone} onChange={(e) => setPhone(e.target.value)} required />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Password</label>
            <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button type="submit" className="w-full" disabled={loading}>{loading ? 'Signing in...' : 'Sign In'}</Button>
        </form>
        <p className="mt-6 text-center text-sm text-gray-500">
          No account? <Link href="/register" className="font-medium text-brand-600 hover:underline">Register</Link>
        </p>
      </Card>
    </div>
  )
}
