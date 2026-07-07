import { useEffect, useState } from 'react'
import { RefreshCw, CheckCircle, AlertTriangle } from 'lucide-react'
import DataTable from '../components/DataTable'

export default function UpdatesPage({ token }: { token: string }) {
  const [updates, setUpdates] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/v1/updates', { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then(setUpdates)
      .finally(() => setLoading(false))
  }, [token])

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'version', label: 'Version' },
    { key: 'release_notes', label: 'Notes', render: (v: string) => (
      <span className="text-gray-400 max-w-xs truncate block">{v}</span>
    )},
    { key: 'status', label: 'Status', render: (v: string) => (
      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs ${
        v === 'applied' ? 'bg-green-600/20 text-green-400' :
        v === 'failed' ? 'bg-red-600/20 text-red-400' :
        'bg-blue-600/20 text-blue-400'
      }`}>
        {v === 'applied' ? <CheckCircle size={12} /> :
         v === 'failed' ? <AlertTriangle size={12} /> :
         <RefreshCw size={12} />}
        {v}
      </span>
    )},
    { key: 'applied_at', label: 'Applied', render: (v: string) => v ? new Date(v).toLocaleDateString() : '-' },
  ]

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold mb-1">Updates</h2>
          <p className="text-sm text-gray-500">Firmware and system updates</p>
        </div>
        <button className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
          <RefreshCw size={16} /> Check for Updates
        </button>
      </div>
      <div className="bg-[#1e2139] rounded-xl border border-[#2a2d3e] p-4">
        <DataTable columns={columns} data={updates} loading={loading} />
      </div>
    </div>
  )
}
