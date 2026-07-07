import { useEffect, useState } from 'react'
import DataTable from '../components/DataTable'

export default function SubscriptionsPage({ token }: { token: string }) {
  const [subscriptions, setSubscriptions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/v1/subscriptions', { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then(setSubscriptions)
      .finally(() => setLoading(false))
  }, [token])

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'user', label: 'User', render: (v: any) => v?.name ?? '-' },
    { key: 'plan', label: 'Plan' },
    { key: 'status', label: 'Status', render: (v: string) => (
      <span className={`inline-flex px-2 py-0.5 rounded-full text-xs ${
        v === 'active' ? 'bg-green-600/20 text-green-400' :
        v === 'expired' ? 'bg-red-600/20 text-red-400' :
        'bg-yellow-600/20 text-yellow-400'
      }`}>{v}</span>
    )},
    { key: 'start_date', label: 'Start', render: (v: string) => v ? new Date(v).toLocaleDateString() : '-' },
    { key: 'end_date', label: 'End', render: (v: string) => v ? new Date(v).toLocaleDateString() : '-' },
  ]

  return (
    <div>
      <h2 className="text-2xl font-bold mb-1">Subscriptions</h2>
      <p className="text-sm text-gray-500 mb-6">User subscription management</p>
      <div className="bg-[#1e2139] rounded-xl border border-[#2a2d3e] p-4">
        <DataTable columns={columns} data={subscriptions} loading={loading} />
      </div>
    </div>
  )
}
