'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/auth'
import { cn } from '@/lib/utils'

const customerNav = [
  { href: '/dashboard', label: 'Home' },
  { href: '/buy-gas', label: 'Buy Gas' },
  { href: '/meters', label: 'My Meters' },
  { href: '/transactions', label: 'Transactions' },
  { href: '/tokens', label: 'Tokens' },
  { href: '/profile', label: 'Profile' },
]

const adminNav = [
  { href: '/admin', label: 'Dashboard' },
  { href: '/admin/customers', label: 'Customers' },
  { href: '/admin/meters', label: 'Meters' },
  { href: '/admin/transactions', label: 'Transactions' },
  { href: '/admin/reports', label: 'Reports' },
  { href: '/admin/settings', label: 'Settings' },
]

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const router = useRouter()
  const { user, logout } = useAuthStore()
  const nav = user?.role === 'admin' || user?.role === 'distributor' ? adminNav : customerNav

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-50 border-b border-gray-200 bg-white/90 backdrop-blur dark:border-gray-800 dark:bg-gray-950/90">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <div className="flex items-center gap-8">
            <Link href="/dashboard" className="flex items-center gap-3 text-xl font-bold text-brand-700">
              <div className="w-9 h-9 rounded-full bg-brand-600 text-white flex items-center justify-center text-sm font-bold">PG</div>
              <span className="text-lg text-brand-700">PrepaidGas Kenya</span>
            </Link>
            <nav className="hidden gap-1 md:flex">
              {nav.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                    pathname === item.href ? 'bg-brand-50 text-brand-700' : 'text-gray-600 hover:text-gray-900'
                  )}
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden text-sm text-gray-500 sm:block">{user?.first_name || user?.phone_number}</span>
            <button onClick={() => { logout(); router.push('/login') }} className="btn-secondary text-sm">Logout</button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-8">{children}</main>
    </div>
  )
}
