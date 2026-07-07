interface Column {
  key: string
  label: string
  render?: (value: any, row: any) => React.ReactNode
}

interface DataTableProps {
  columns: Column[]
  data: any[]
  loading?: boolean
}

export default function DataTable({ columns, data, loading }: DataTableProps) {
  if (loading) {
    return (
      <div className="text-center py-12 text-gray-500">
        <div className="animate-spin w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full mx-auto mb-2" />
        Loading...
      </div>
    )
  }

  if (!data.length) {
    return <div className="text-center py-12 text-gray-500">No data found</div>
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-[#2a2d3e]">
            {columns.map((c) => (
              <th key={c.key} className="text-left py-3 px-4 text-gray-400 font-medium">
                {c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={row.id ?? i} className="border-b border-[#2a2d3e] hover:bg-[#1e2139] transition-colors">
              {columns.map((c) => (
                <td key={c.key} className="py-3 px-4">
                  {c.render ? c.render(row[c.key], row) : row[c.key] ?? '-'}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
