'use client'

import { useQuery } from '@tanstack/react-query'
import { AppShell } from '@/components/app-shell'
import { Card } from '@/components/ui'
import { adminApi } from '@/lib/api'

type IntegrationStatus = {
  mpesa: { configured: boolean; missing: string[]; env: string; shortcode: string; callback_url: string }
  stron: { configured: boolean; missing: string[]; base_url: string; vend_by_unit: boolean }
  ready_for_purchase: boolean
}

function StatusBadge({ ok }: { ok: boolean }) {
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${ok ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
      {ok ? 'Configured' : 'Missing'}
    </span>
  )
}

export default function AdminSettingsPage() {
  const { data: status, isLoading, error } = useQuery({
    queryKey: ['integration-status'],
    queryFn: () => adminApi.integrations().then((r) => r.data as IntegrationStatus),
  })

  return (
    <AppShell>
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Admin — Settings</h1>
        <p className="text-gray-500">Platform configuration and integration status</p>
      </div>

      {isLoading && <p className="text-sm text-gray-500">Checking configuration…</p>}
      {error && (
        <Card className="mb-6 border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Could not load integration status. Ensure you are logged in as admin.
        </Card>
      )}

      {status && !status.ready_for_purchase && (
        <Card className="mb-6 border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          Purchases are blocked until M-Pesa and Stron credentials are set in <code className="font-mono">backend/.env</code> on the server,
          then containers are restarted with <code className="font-mono">docker compose up -d --build</code>.
        </Card>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold">M-Pesa</h2>
            {status && <StatusBadge ok={status.mpesa.configured} />}
          </div>
          <div className="space-y-4 text-sm">
            <div>
              <p className="text-gray-500">Environment</p>
              <p className="font-medium">{status?.mpesa.env || 'sandbox'}</p>
            </div>
            <div>
              <p className="text-gray-500">Shortcode</p>
              <p className="font-mono font-medium">{status?.mpesa.shortcode || '174379'}</p>
            </div>
            <div>
              <p className="text-gray-500">Callback URL</p>
              <p className="break-all font-mono text-xs">{status?.mpesa.callback_url || '—'}</p>
            </div>
            {status?.mpesa.missing.length ? (
              <div>
                <p className="text-gray-500">Missing env vars</p>
                <p className="font-mono text-red-600">{status.mpesa.missing.join(', ')}</p>
              </div>
            ) : null}
          </div>
        </Card>

        <Card className="p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Stron Power API</h2>
            {status && <StatusBadge ok={status.stron.configured} />}
          </div>
          <div className="space-y-4 text-sm">
            <div>
              <p className="text-gray-500">Base URL</p>
              <p className="break-all font-mono text-xs">{status?.stron.base_url || '—'}</p>
            </div>
            <div>
              <p className="text-gray-500">Vend By Unit</p>
              <p className="font-medium">{status?.stron.vend_by_unit ? 'Enabled' : 'Disabled (vend by KES)'}</p>
            </div>
            {status?.stron.missing.length ? (
              <div>
                <p className="text-gray-500">Missing env vars</p>
                <p className="font-mono text-red-600">{status.stron.missing.join(', ')}</p>
              </div>
            ) : null}
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="mb-4 text-lg font-semibold">Purchase Limits</h2>
          <div className="space-y-4 text-sm">
            <div>
              <p className="text-gray-500">Minimum</p>
              <p className="font-medium">KES 50</p>
            </div>
            <div>
              <p className="text-gray-500">Maximum</p>
              <p className="font-medium">KES 50,000</p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="mb-4 text-lg font-semibold">Notifications</h2>
          <div className="space-y-4 text-sm">
            <div>
              <p className="text-gray-500">SMS Provider</p>
              <p className="font-medium">Africa&apos;s Talking</p>
            </div>
            <div>
              <p className="text-gray-500">Email Provider</p>
              <p className="font-medium">SMTP / SendGrid</p>
            </div>
          </div>
        </Card>
      </div>
    </AppShell>
  )
}
