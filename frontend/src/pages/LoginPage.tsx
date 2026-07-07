import { useState } from 'react'
import { Printer } from 'lucide-react'

interface LoginProps {
  onLogin: (token: string, user: any) => void
}

export default function LoginPage({ onLogin }: LoginProps) {
  const [email, setEmail] = useState('admin@satelecom.com')
  const [password, setPassword] = useState('admin')
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    try {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      const data = await res.json()
      if (!res.ok) {
        setError(data.detail || 'Login failed')
        return
      }

      onLogin(data.access_token, data.user)
    } catch {
      setError('Cannot connect to server')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f1117]">
      <div className="bg-[#1a1d2e] p-8 rounded-2xl border border-[#2a2d3e] w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="inline-flex p-3 bg-indigo-600/10 rounded-xl mb-4">
            <Printer className="text-indigo-400" size={32} />
          </div>
          <h1 className="text-xl font-bold">SATelecom CutOS</h1>
          <p className="text-sm text-gray-500 mt-1">Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-[#0f1117] border border-[#2a2d3e] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 text-white"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-[#0f1117] border border-[#2a2d3e] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 text-white"
              required
            />
          </div>

          {error && <p className="text-red-400 text-sm">{error}</p>}

          <button
            type="submit"
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg py-2 text-sm font-medium transition-colors"
          >
            Sign In
          </button>
        </form>
      </div>
    </div>
  )
}
