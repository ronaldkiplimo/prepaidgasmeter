'use client'

import { useQuery } from '@tanstack/react-query'
import { AppShell } from '@/components/app-shell'
import { Card, Button } from '@/components/ui'
import { tokensApi } from '@/lib/api'

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString()
}

function copyToClipboard(text: string) {
  navigator.clipboard.writeText(text)
  alert('Token copied to clipboard!')
}

export default function TokensPage() {
  const { data: tokens, isLoading } = useQuery({
    queryKey: ['tokens'],
    queryFn: () => tokensApi.history().then((r) => r.data.results || r.data),
  })

  return (
    <AppShell>
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Tokens</h1>
        <p className="text-gray-500">Your purchased gas tokens</p>
      </div>

      {isLoading ? (
        <Card className="p-8 text-center text-gray-500">Loading tokens...</Card>
      ) : tokens?.length === 0 ? (
        <Card className="p-8 text-center">
          <p className="text-gray-500">No tokens yet. Buy gas to generate your first token!</p>
        </Card>
      ) : (
        <div className="space-y-4">
          {tokens.map((token: any) => (
            <Card key={token.id} className="p-6">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-3">
                    <h3 className="font-semibold font-mono">{token.token}</h3>
                    <Button variant="secondary" onClick={() => copyToClipboard(token.token)}>
                      Copy
                    </Button>
                  </div>
                  <p className="mt-1 text-sm text-gray-500">
                    Meter: {token.meter_number} • {formatDate(token.generated_at)}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold">{token.token_units} units</p>
                  <p className="text-sm text-gray-600">KES {token.token_amount}</p>
                </div>
              </div>

              {token.stron_receipt_number && (
                <div className="mt-4 rounded-lg bg-gray-50 p-3 text-sm">
                  <p className="text-gray-600">
                    Stron Receipt: <span className="font-mono">{token.stron_receipt_number}</span>
                  </p>
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </AppShell>
  )
}
