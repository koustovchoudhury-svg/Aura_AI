import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AURA AI-OS',
  description: 'Autonomous Unified Responsive Assistant — Your Personal AI Operating System',
  icons: { icon: '/favicon.ico' }
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#0f0f23] text-gray-100 min-h-screen">
        {children}
      </body>
    </html>
  )
}
