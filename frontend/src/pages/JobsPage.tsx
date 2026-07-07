import { useEffect, useState } from 'react'
import DataTable from '../components/DataTable'

export default function JobsPage({ token }: { token: string }) {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/v1/jobs', { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then(setJobs)
      .finally(() => setLoading(false))
  }, [token])

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'template', label: 'Template', render: (v: any) => v?.name ?? '-' },
    { key: 'machine', label: 'Machine', render: (v: any) => v?.name ?? '-' },
    { key: 'user', label: 'User', render: (v: any) => v?.name ?? '-' },
    { key: 'status', label: 'Status', render: (v: string) => (
      <span className={`inline-flex px-2 py-0.5 rounded-full text-xs ${
        v === 'completed' ? 'bg-green-600/20 text-green-400' :
        v === 'failed' ? 'bg-red-600/20 text-red-400' :
        v === 'printing' ? 'bg-blue-600/20 text-blue-400' :
        'bg-yellow-600/20 text-yellow-400'
      }`}>{v}</span>
    )},
    { key: 'created_at', label: 'Created', render: (v: string) => new Date(v).toLocaleString() },
  ]

  return (
    <div>
      <h2 className="text-2xl font-bold mb-1">Jobs</h2>
      <p className="text-sm text-gray-500 mb-6">Print and cut job history</p>
      <div className="bg-[#1e2139] rounded-xl border border-[#2a2d3e] p-4">
        <DataTable columns={columns} data={jobs} loading={loading} />
      </div>
    </div>
  )
}
