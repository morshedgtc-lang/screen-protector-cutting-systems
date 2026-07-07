import { useEffect, useState } from 'react'
import { Plus } from 'lucide-react'
import DataTable from '../components/DataTable'

export default function UsersPage({ token }: { token: string }) {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/v1/users', { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then(setUsers)
      .finally(() => setLoading(false))
  }, [token])

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'name', label: 'Name' },
    { key: 'email', label: 'Email' },
    { key: 'role', label: 'Role', render: (v: string) => <span className="capitalize">{v}</span> },
    { key: 'is_active', label: 'Active', render: (v: boolean) => (v ? 'Yes' : 'No') },
    { key: 'created_at', label: 'Created', render: (v: string) => new Date(v).toLocaleDateString() },
  ]

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">Users</h2>
          <p className="text-sm text-gray-500 mt-1">Manage system users</p>
        </div>
        <button className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
          <Plus size={16} /> Add User
        </button>
      </div>
      <div className="bg-[#1e2139] rounded-xl border border-[#2a2d3e] p-4">
        <DataTable columns={columns} data={users} loading={loading} />
      </div>
    </div>
  )
}
