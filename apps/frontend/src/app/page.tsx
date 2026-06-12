'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function Home() {
  const router = useRouter()
  useEffect(() => {
    const token = localStorage.getItem('aura_token')
    router.replace(token ? '/chat' : '/login')
  }, [router])

  return (
    <div className="flex items-center justify-center h-screen">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-purple-600 flex items-center justify-center animate-pulse">
          <span className="text-white font-bold text-lg">A</span>
        </div>
        <span className="text-gray-400 text-lg">Initialising AURA...</span>
      </div>
    </div>
  )
}
