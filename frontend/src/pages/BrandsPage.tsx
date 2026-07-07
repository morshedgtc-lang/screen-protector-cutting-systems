import { useEffect, useState } from 'react'
import DataTable from '../components/DataTable'

export default function BrandsPage({ token }: { token: string }) {
  const [brands, setBrands] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/v1/brands', { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then(setBrands)
      .finally(() => setLoading(false))
  }, [token])

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'name', label: 'Brand' },
    { key: 'category', label: 'Category', render: (v: any) => v?.name ?? '-' },
    { key: 'series_count', label: 'Series', render: (_: any, row: any) => row.series?.length ?? 0 },
    { key: 'model_count', label: 'Models', render: (_: any, row: any) =>
      row.series?.reduce((s: number, ser: any) => s + (ser.models?.length ?? 0), 0) ?? 0 },
    { key: 'is_active', label: 'Active', render: (v: boolean) => (v ? 'Yes' : 'No') },
  ]

  return (
    <div>
      <h2 className="text-2xl font-bold mb-1">Brands & Models</h2>
      <p className="text-sm text-gray-500 mb-6">Phone brand and model catalog</p>
      <div className="bg-[#1e2139] rounded-xl border border-[#2a2d3e] p-4">
        <DataTable columns={columns} data={brands} loading={loading} />
      </div>
    </div>
  )
}
