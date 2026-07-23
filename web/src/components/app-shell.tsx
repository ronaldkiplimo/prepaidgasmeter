'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { BarChart3, CreditCard, Gauge, Home, LogOut, Settings, Ticket, Users, WalletCards } from 'lucide-react'
import { useAuthStore } from '@/store/auth'
import { cn } from '@/lib/utils'

const customerNav = [
  { href: '/dashboard', label: 'Home', icon: Home },
  { href: '/buy-gas', label: 'Buy Gas', icon: CreditCard },
  { href: '/meters', label: 'Meters', icon: Gauge },
  { href: '/transactions', label: 'Transactions', icon: WalletCards },
  { href: '/tokens', label: 'Tokens', icon: Ticket },
  { href: '/profile', label: 'Profile', icon: Settings },
]

const adminNav = [
  { href: '/admin', label: 'Dashboard', icon: Home },
  { href: '/admin/customers', label: 'Customers', icon: Users },
  { href: '/admin/meters', label: 'Meters', icon: Gauge },
  { href: '/admin/transactions', label: 'Transactions', icon: WalletCards },
  { href: '/admin/reports', label: 'Reports', icon: BarChart3 },
  { href: '/admin/settings', label: 'Settings', icon: Settings },
]

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const router = useRouter()
  const { user, logout } = useAuthStore()
  const nav = user?.role === 'admin' || user?.role === 'distributor' ? adminNav : customerNav

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/95 backdrop-blur dark:border-slate-800 dark:bg-slate-950/95">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <div className="flex items-center gap-8">
            <Link href={user?.role === 'admin' || user?.role === 'distributor' ? '/admin' : '/dashboard'} className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-teal-700 text-sm font-bold text-white">PG</div>
              <div className="leading-tight">
                <span className="block text-base font-bold text-slate-950 dark:text-white">PrepaidGas</span>
                <span className="hidden text-xs font-medium text-slate-500 sm:block">Meter vending console</span>
              </div>
            </Link>
            <nav className="hidden gap-1 md:flex">
              {nav.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold transition-colors',
                    pathname === item.href ? 'bg-teal-50 text-teal-800' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-950 dark:text-slate-300 dark:hover:bg-slate-900'
                  )}
                >
                  <item.icon className="h-4 w-4" />
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden text-right sm:block">
              <span className="block text-sm font-semibold text-slate-800 dark:text-slate-100">{user?.first_name || user?.phone_number}</span>
              <span className="block text-xs capitalize text-slate-500">{user?.role || 'customer'}</span>
            </div>
            <button onClick={() => { logout(); router.push('/login') }} className="btn-secondary text-sm" aria-label="Logout">
              <LogOut className="h-4 w-4" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
        <nav className="mx-auto flex max-w-7xl gap-1 overflow-x-auto border-t border-slate-100 px-4 py-2 md:hidden dark:border-slate-900">
          {nav.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'inline-flex shrink-0 items-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold transition-colors',
                    pathname === item.href ? 'bg-teal-50 text-teal-800' : 'text-slate-600'
                  )}
                >
                  <item.icon className="h-4 w-4" />
                  {item.label}
                </Link>
              ))}
            </nav>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6 sm:py-8">{children}</main>
    </div>
  )
}
