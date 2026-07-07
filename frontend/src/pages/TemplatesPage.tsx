import { useEffect, useState } from 'react'
import { Upload, Plus } from 'lucide-react'
import DataTable from '../components/DataTable'

export default function TemplatesPage({ token }: { token: string }) {
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/v1/templates', { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then(setTemplates)
      .finally(() => setLoading(false))
  }, [token])

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'name', label: 'Name' },
    { key: 'model', label: 'Model', render: (v: any) => v?.name ?? '-' },
    { key: 'file_format', label: 'Format' },
    { key: 'version', label: 'Version' },
    { key: 'is_active', label: 'Active', render: (v: boolean) => (v ? 'Yes' : 'No') },
  ]

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold mb-1">Templates</h2>
          <p className="text-sm text-gray-500">Screen protector cutting templates</p>
        </div>
        <div className="flex gap-2">
          <button className="flex items-center gap-2 border border-[#2a2d3e] hover:bg-[#2a2d3e] text-white px-4 py-2 rounded-lg text-sm transition-colors">
            <Upload size={16} /> Upload
          </button>
          <button className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
            <Plus size={16} /> New Template
          </button>
        </div>
      </div>
      <div className="bg-[#1e2139] rounded-xl border border-[#2a2d3e] p-4">
        <DataTable columns={columns} data={templates} loading={loading} />
      </div>
    </div>
  )
}
