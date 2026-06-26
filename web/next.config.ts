import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  output: 'standalone',
  async rewrites() {
    const backend = process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000'

    return [
      {
        source: '/api/:path*',
        destination: `${backend}/api/:path*`,
      },
      {
        source: '/admin',
        destination: `${backend}/admin/`,
      },
      {
        source: '/admin/:path*',
        destination: `${backend}/admin/:path*`,
      },
      {
        source: '/static/:path*',
        destination: `${backend}/static/:path*`,
      },
      {
        source: '/media/:path*',
        destination: `${backend}/media/:path*`,
      },
    ]
  },
}

export default nextConfig
