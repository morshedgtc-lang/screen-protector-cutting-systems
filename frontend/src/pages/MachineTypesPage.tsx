import { useEffect, useState } from 'react'
import DataTable from '../components/DataTable'

export default function MachineTypesPage({ token }: { token: string }) {
  const [types, setTypes] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/v1/machine-types', { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then(setTypes)
      .finally(() => setLoading(false))
  }, [token])

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'name', label: 'Name' },
    { key: 'manufacturer', label: 'Manufacturer' },
    { key: 'driver_key', label: 'Driver Key' },
    { key: 'supported_formats', label: 'Formats', render: (v: string[]) => v?.join(', ') ?? '-' },
    { key: 'is_active', label: 'Active', render: (v: boolean) => (v ? 'Yes' : 'No') },
  ]

  return (
    <div>
      <h2 className="text-2xl font-bold mb-1">Machine Types</h2>
      <p className="text-sm text-gray-500 mb-6">Supported cutting machine models</p>
      <div className="bg-[#1e2139] rounded-xl border border-[#2a2d3e] p-4">
        <DataTable columns={columns} data={types} loading={loading} />
      </div>
    </div>
  )
}
