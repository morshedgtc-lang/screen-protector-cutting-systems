import { Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import UsersPage from './pages/UsersPage'
import MachinesPage from './pages/MachinesPage'
import MachineTypesPage from './pages/MachineTypesPage'
import TemplatesPage from './pages/TemplatesPage'
import BrandsPage from './pages/BrandsPage'
import JobsPage from './pages/JobsPage'
import SubscriptionsPage from './pages/SubscriptionsPage'
import SettingsPage from './pages/SettingsPage'
import UpdatesPage from './pages/UpdatesPage'
import LogsPage from './pages/LogsPage'
import DownloadsPage from './pages/DownloadsPage'
import MachineTerminal from './pages/MachineTerminal'

interface User {
  id: number
  email: string
  name: string
  role: string
}

function App() {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))

  useEffect(() => {
    if (token) {
      fetch('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((r) => (r.ok ? r.json() : null))
        .then((data) => {
          if (data) setUser(data)
          else {
            localStorage.removeItem('token')
            setToken(null)
          }
        })
        .catch(() => {
          localStorage.removeItem('token')
          setToken(null)
        })
    }
  }, [token])

  // Machine terminal is public (no auth required)
  if (window.location.pathname === '/terminal') {
    return <MachineTerminal />
  }

  if (!token || !user) {
    return <LoginPage onLogin={(t, u) => { setToken(t); setUser(u); localStorage.setItem('token', t) }} />
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar user={user} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header user={user} onLogout={() => { setToken(null); setUser(null); localStorage.removeItem('token') }} />
        <main className="flex-1 overflow-y-auto p-6">
          <Routes>
            <Route path="/" element={<DashboardPage token={token} />} />
            <Route path="/users" element={<UsersPage token={token} />} />
            <Route path="/machines" element={<MachinesPage token={token} />} />
            <Route path="/machine-types" element={<MachineTypesPage token={token} />} />
            <Route path="/templates" element={<TemplatesPage token={token} />} />
            <Route path="/brands" element={<BrandsPage token={token} />} />
            <Route path="/jobs" element={<JobsPage token={token} />} />
            <Route path="/subscriptions" element={<SubscriptionsPage token={token} />} />
            <Route path="/settings" element={<SettingsPage token={token} />} />
            <Route path="/updates" element={<UpdatesPage token={token} />} />
            <Route path="/logs" element={<LogsPage token={token} />} />
            <Route path="/downloads" element={<DownloadsPage token={token} />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default App
