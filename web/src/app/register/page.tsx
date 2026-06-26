'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { authApi, getApiErrorMessage } from '@/lib/api'
import { useAuthStore } from '@/store/auth'
import { Button, Card, Input } from '@/components/ui'

export default function RegisterPage() {
  const router = useRouter()
  const { setAuth } = useAuthStore()
  const [form, setForm] = useState({
    username: '', email: '', phone_number: '', password: '', password_confirm: '',
    first_name: '', last_name: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (form.password !== form.password_confirm) { setError('Passwords do not match'); return }
    setLoading(true)
    try {
      const { data } = await authApi.register(form)
      setAuth(data.user, data.tokens.access, data.tokens.refresh)
      router.push('/dashboard')
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, 'Registration failed. Check your details.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-brand-700 to-brand-900 px-4 py-8">
      <Card className="w-full max-w-lg p-8 shadow-md">
        <div className="mb-6 text-center">
          <div className="flex items-center justify-center gap-3">
            <div className="w-12 h-12 rounded-full bg-brand-600 text-white flex items-center justify-center text-lg font-bold">PG</div>
            <h1 className="text-2xl font-bold text-gray-900">Create Account</h1>
          </div>
        </div>
        <form onSubmit={handleSubmit} className="grid gap-4 sm:grid-cols-2">
          <Input placeholder="First name" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} required />
          <Input placeholder="Last name" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} required />
          <Input className="sm:col-span-2" placeholder="Username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} required />
          <Input className="sm:col-span-2" type="email" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          <Input className="sm:col-span-2" type="tel" placeholder="254712345678" value={form.phone_number} onChange={(e) => setForm({ ...form, phone_number: e.target.value })} required />
          <Input type="password" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
          <Input type="password" placeholder="Confirm" value={form.password_confirm} onChange={(e) => setForm({ ...form, password_confirm: e.target.value })} required />
          {error && <p className="sm:col-span-2 text-sm text-red-600">{error}</p>}
          <Button type="submit" className="sm:col-span-2 w-full" disabled={loading}>Register</Button>
        </form>
        <p className="mt-4 text-center text-sm"><Link href="/login" className="text-brand-600 hover:underline">Already have an account?</Link></p>
      </Card>
    </div>
  )
}
