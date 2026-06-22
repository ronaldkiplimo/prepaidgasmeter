import { cn } from '@/lib/utils'

export function Button({ className, variant = 'primary', ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' }) {
  return <button className={cn(variant === 'primary' ? 'btn-primary' : 'btn-secondary', className)} {...props} />
}

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('card', className)} {...props} />
}

export function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input className="input" {...props} />
}

export function StatCard({ label, value, accent }: { label: string; value: string | number; accent?: string }) {
  return (
    <Card>
      <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
      <p className={cn('mt-1 text-2xl font-bold', accent)}>{value}</p>
    </Card>
  )
}
