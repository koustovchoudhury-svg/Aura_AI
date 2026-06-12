'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'

export default function LoginPage() {
  const router   = useRouter()
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState('')
  const [mode, setMode]         = useState<'login'|'register'>('login')
  const [name, setName]         = useState('')

  const handleSubmit = async () => {
    setLoading(true); setError('')
    const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    try {
      if (mode === 'register') {
        await axios.post(`${API}/api/auth/register`, { email, name, password })
      }
      const params = new URLSearchParams({ username: email, password })
      const { data } = await axios.post(`${API}/api/auth/token`, params,
        { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
      localStorage.setItem('aura_token',   data.access_token)
      localStorage.setItem('aura_user_id', data.user_id)
      localStorage.setItem('aura_name',    data.name)
      router.replace('/chat')
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Authentication failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-[#0f0f23] px-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-purple-600 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-purple-900/50">
            <span className="text-white font-black text-2xl">A</span>
          </div>
          <h1 className="text-2xl font-bold text-white">AURA AI-OS</h1>
          <p className="text-gray-500 text-sm mt-1">Your Personal AI Operating System</p>
        </div>

        {/* Form */}
        <div className="bg-[#1a1a2e] border border-[#2a2a4a] rounded-2xl p-6 space-y-4">
          {mode === 'register' && (
            <input
              type="text"
              placeholder="Full name"
              value={name}
              onChange={e => setName(e.target.value)}
              className="w-full bg-[#0f0f23] border border-[#2a2a4a] rounded-xl px-4 py-3
                         text-white placeholder-gray-600 text-sm outline-none
                         focus:border-purple-500 transition-colors"
            />
          )}
          <input
            type="email"
            placeholder="Email address"
            value={email}
            onChange={e => setEmail(e.target.value)}
            className="w-full bg-[#0f0f23] border border-[#2a2a4a] rounded-xl px-4 py-3
                       text-white placeholder-gray-600 text-sm outline-none
                       focus:border-purple-500 transition-colors"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSubmit()}
            className="w-full bg-[#0f0f23] border border-[#2a2a4a] rounded-xl px-4 py-3
                       text-white placeholder-gray-600 text-sm outline-none
                       focus:border-purple-500 transition-colors"
          />

          {error && (
            <p className="text-red-400 text-sm bg-red-900/20 border border-red-800/50
                          rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          <button
            onClick={handleSubmit}
            disabled={loading || !email || !password}
            className="w-full bg-purple-600 hover:bg-purple-500 disabled:opacity-40
                       disabled:cursor-not-allowed text-white font-semibold
                       rounded-xl py-3 text-sm transition-all"
          >
            {loading ? 'Please wait...' : mode === 'login' ? 'Sign in' : 'Create account'}
          </button>
        </div>

        <p className="text-center text-gray-600 text-sm mt-4">
          {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
          <button
            onClick={() => setMode(m => m === 'login' ? 'register' : 'login')}
            className="text-purple-400 hover:text-purple-300 transition-colors"
          >
            {mode === 'login' ? 'Create one' : 'Sign in'}
          </button>
        </p>

        <p className="text-center text-gray-700 text-xs mt-6">
          Default: admin@aura.local / aura_admin_2024
        </p>
      </div>
    </div>
  )
}
