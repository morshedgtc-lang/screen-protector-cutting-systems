import { useEffect, useState } from 'react'
import { Users, Printer, FileType, ListChecks, Activity } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import StatCard from '../components/StatCard'

export default function DashboardPage({ token }: { token: string }) {
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    fetch('/api/v1/analytics/dashboard', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => (r.ok ? r.json() : null))
      .then(setStats)
  }, [token])

  const cards = [
    { title: 'Total Users', value: stats?.total_users ?? '—', icon: Users },
    { title: 'Active Machines', value: stats?.active_machines ?? '—', icon: Printer },
    { title: 'Templates', value: stats?.total_templates ?? '—', icon: FileType },
    { title: 'Jobs Today', value: stats?.jobs_today ?? '—', icon: ListChecks },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Dashboard</h2>
        <p className="text-sm text-gray-500 mt-1">System overview and metrics</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((c) => (
          <StatCard key={c.title} {...c} color="text-indigo-400" />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {stats?.daily_jobs && (
          <div className="bg-[#1e2139] rounded-xl p-5 border border-[#2a2d3e]">
            <h3 className="text-sm font-medium mb-4 flex items-center gap-2">
              <Activity size={16} className="text-indigo-400" />
              Jobs (Last 14 Days)
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={stats.daily_jobs}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3e" />
                <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} />
                <YAxis stroke="#9ca3af" fontSize={12} />
                <Tooltip
                  contentStyle={{ background: '#1a1d2e', border: '1px solid #2a2d3e', borderRadius: 8 }}
                  labelStyle={{ color: '#e8e8e8' }}
                />
                <Line type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        <div className="bg-[#1e2139] rounded-xl p-5 border border-[#2a2d3e]">
          <h3 className="text-sm font-medium mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {(stats?.recent_activity ?? []).length === 0 ? (
              <p className="text-sm text-gray-500">No recent activity</p>
            ) : (
              stats?.recent_activity?.map((a: any, i: number) => (
                <div key={i} className="flex items-center gap-3 text-sm">
                  <div className="w-2 h-2 rounded-full bg-indigo-500" />
                  <span className="text-gray-400">{a.action}</span>
                  <span className="text-gray-600 ml-auto">{new Date(a.timestamp).toLocaleString()}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
