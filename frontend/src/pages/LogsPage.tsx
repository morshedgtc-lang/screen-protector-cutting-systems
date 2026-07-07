import { useEffect, useState } from 'react'
import { Search, Download } from 'lucide-react'

export default function LogsPage({ token }: { token: string }) {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [level, setLevel] = useState('')

  useEffect(() => {
    const params = new URLSearchParams()
    if (level) params.set('level', level)
    fetch(`/api/v1/logs?${params}`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then(setLogs)
      .finally(() => setLoading(false))
  }, [token, level])

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold mb-1">Logs</h2>
          <p className="text-sm text-gray-500">System audit logs</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={level}
            onChange={(e) => setLevel(e.target.value)}
            className="bg-[#0f1117] border border-[#2a2d3e] rounded-lg px-3 py-2 text-sm text-gray-300"
          >
            <option value="">All Levels</option>
            <option value="INFO">INFO</option>
            <option value="WARNING">WARNING</option>
            <option value="ERROR">ERROR</option>
            <option value="DEBUG">DEBUG</option>
          </select>
          <button className="flex items-center gap-2 border border-[#2a2d3e] hover:bg-[#2a2d3e] px-4 py-2 rounded-lg text-sm transition-colors">
            <Download size={16} /> Export
          </button>
        </div>
      </div>

      <div className="bg-[#1e2139] rounded-xl border border-[#2a2d3e]">
        <div className="p-4 border-b border-[#2a2d3e]">
          <div className="flex items-center gap-2 bg-[#0f1117] rounded-lg px-3 py-2">
            <Search size={16} className="text-gray-500" />
            <input
              placeholder="Search logs..."
              className="bg-transparent border-none outline-none text-sm text-gray-300 w-full"
            />
          </div>
        </div>
        <div className="p-4">
          {loading ? (
            <div className="text-center py-8 text-gray-500">Loading...</div>
          ) : logs.length === 0 ? (
            <div className="text-center py-8 text-gray-500">No logs found</div>
          ) : (
            <div className="space-y-2 font-mono text-xs">
              {logs.map((log: any, i: number) => (
                <div key={i} className={`flex gap-3 p-2 rounded ${
                  log.level === 'ERROR' ? 'bg-red-600/10 text-red-400' :
                  log.level === 'WARNING' ? 'bg-yellow-600/10 text-yellow-400' :
                  'text-gray-400'
                }`}>
                  <span className="text-gray-600 shrink-0">{new Date(log.timestamp).toISOString()}</span>
                  <span className="shrink-0 font-bold">[{log.level}]</span>
                  <span>{log.message}</span>
                  {log.user && <span className="text-gray-600 ml-auto">by {log.user.name}</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
