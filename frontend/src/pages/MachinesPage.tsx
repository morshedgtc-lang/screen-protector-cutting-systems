import { useEffect, useState } from 'react'
import DataTable from '../components/DataTable'

export default function MachinesPage({ token }: { token: string }) {
  const [machines, setMachines] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/v1/machines', { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then(setMachines)
      .finally(() => setLoading(false))
  }, [token])

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'name', label: 'Name' },
    { key: 'machine_type', label: 'Type', render: (v: any) => v?.name ?? '-' },
    { key: 'status', label: 'Status', render: (v: string) => (
      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs ${
        v === 'online' ? 'bg-green-600/20 text-green-400' : 'bg-gray-600/20 text-gray-400'
      }`}>
        <span className={`w-1.5 h-1.5 rounded-full ${v === 'online' ? 'bg-green-400' : 'bg-gray-400'}`} />
        {v ?? 'offline'}
      </span>
    )},
    { key: 'firmware_version', label: 'Firmware' },
    { key: 'last_seen', label: 'Last Seen', render: (v: string) => v ? new Date(v).toLocaleString() : '-' },
  ]

  return (
    <div>
      <h2 className="text-2xl font-bold mb-1">Machines</h2>
      <p className="text-sm text-gray-500 mb-6">Connected cutting machines</p>
      <div className="bg-[#1e2139] rounded-xl border border-[#2a2d3e] p-4">
        <DataTable columns={columns} data={machines} loading={loading} />
      </div>
    </div>
  )
}
