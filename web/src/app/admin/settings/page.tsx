'use client'

import { AppShell } from '@/components/app-shell'
import { Card } from '@/components/ui'

export default function AdminSettingsPage() {
  return (
    <AppShell>
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Admin — Settings</h1>
        <p className="text-gray-500">Platform configuration</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="p-6">
          <h2 className="mb-4 text-lg font-semibold">System Settings</h2>
          <div className="space-y-4 text-sm">
            <div>
              <p className="text-gray-500">Minimum Purchase Amount</p>
              <p className="font-medium">KES 50</p>
            </div>
            <div>
              <p className="text-gray-500">Maximum Purchase Amount</p>
              <p className="font-medium">KES 50,000</p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="mb-4 text-lg font-semibold">M-Pesa Configuration</h2>
          <div className="space-y-4 text-sm">
            <div>
              <p className="text-gray-500">Environment</p>
              <p className="font-medium">Sandbox</p>
            </div>
            <div>
              <p className="text-gray-500">Shortcode</p>
              <p className="font-mono font-medium">174379</p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="mb-4 text-lg font-semibold">Stron Power API</h2>
          <div className="space-y-4 text-sm">
            <div>
              <p className="text-gray-500">API Version</p>
              <p className="font-medium">3.0.17</p>
            </div>
            <div>
              <p className="text-gray-500">Vend By Unit</p>
              <p className="font-medium">Disabled</p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="mb-4 text-lg font-semibold">Notifications</h2>
          <div className="space-y-4 text-sm">
            <div>
              <p className="text-gray-500">SMS Provider</p>
              <p className="font-medium">Africa's Talking</p>
            </div>
            <div>
              <p className="text-gray-500">Email Provider</p>
              <p className="font-medium">Console (Debug)</p>
            </div>
          </div>
        </Card>
      </div>
    </AppShell>
  )
}
