import { useEffect, useState } from 'react'
import { Download, Smartphone, Globe, Wifi, FolderOpen, Grid, Printer } from 'lucide-react'
import DataTable from '../components/DataTable'

const APPS = [
  { url: '/CutOS-Terminal-Cloud.apk', icon: Globe, label: 'CutOS Terminal (Cloud)', desc: 'Modified OEM app — connects to Railway cloud server. Use if the machine can reach the internet.', size: '7.7 MB', color: 'indigo' },
  { url: '/CutOS-Terminal-Local.apk', icon: Wifi, label: 'CutOS Terminal (Local)', desc: 'Modified OEM app — connects to local server at 192.168.0.100:8000. Use for fully offline operation.', size: '7.7 MB', color: 'green' },
  { url: '/launcher.apk', icon: Grid, label: 'Launcher', desc: 'Custom launcher/home screen. Install first to break out of kiosk mode and access other apps.', size: '11.0 MB', color: 'purple' },
  { url: '/filemanager.apk', icon: FolderOpen, label: 'File Manager', desc: 'File manager for browsing and managing files on the machine. Install after launcher.', size: '8.9 MB', color: 'orange' },
]

export default function DownloadsPage({ token, publicView }: { token?: string; publicView?: boolean }) {
  const [downloads, setDownloads] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (publicView || !token) {
      setLoading(false)
      return
    }
    fetch('/api/v1/downloads', { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then(setDownloads)
      .finally(() => setLoading(false))
  }, [token, publicView])

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'name', label: 'File' },
    { key: 'type', label: 'Type' },
    { key: 'size', label: 'Size', render: (v: number) => {
      if (!v) return '-'
      if (v < 1024) return `${v} B`
      if (v < 1048576) return `${(v / 1024).toFixed(1)} KB`
      return `${(v / 1048576).toFixed(1)} MB`
    }},
    { key: 'download_count', label: 'Downloads' },
    { key: 'version', label: 'Version' },
    { key: 'created_at', label: 'Added', render: (v: string) => v ? new Date(v).toLocaleDateString() : '-' },
    { key: 'id', label: '', render: (_: any, row: any) => (
      <button className="text-indigo-400 hover:text-indigo-300 transition-colors" title="Download">
        <Download size={16} />
      </button>
    )},
  ]

  const colorMap: Record<string, { bg: string, border: string, icon: string }> = {
    indigo: { bg: 'from-indigo-900/40 to-purple-900/40', border: 'border-indigo-800/50', icon: 'bg-indigo-600/20 text-indigo-400' },
    green: { bg: 'from-green-900/40 to-emerald-900/40', border: 'border-green-800/50', icon: 'bg-green-600/20 text-green-400' },
    purple: { bg: 'from-purple-900/40 to-pink-900/40', border: 'border-purple-800/50', icon: 'bg-purple-600/20 text-purple-400' },
    orange: { bg: 'from-orange-900/40 to-amber-900/40', border: 'border-orange-800/50', icon: 'bg-orange-600/20 text-orange-400' },
  }

  return (
    <div>
      {publicView && (
        <div className="flex items-center gap-3 mb-6">
          <Printer className="text-indigo-400" size={28} />
          <div>
            <h2 className="text-xl font-bold">SATelecom CutOS</h2>
            <p className="text-xs text-gray-500">Download APK files to install on the cutting machine</p>
          </div>
        </div>
      )}
      {!publicView && (
        <>
          <h2 className="text-2xl font-bold mb-1">Downloads</h2>
          <p className="text-sm text-gray-500 mb-6">Firmware, software, and template downloads</p>
        </>
      )}

      <div className="space-y-4 mb-8">
        {APPS.map((app) => {
          const c = colorMap[app.color]
          const Icon = app.icon
          return (
            <div key={app.url} className={`bg-gradient-to-r ${c.bg} rounded-xl border ${c.border} p-5`}>
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-xl ${c.icon}`}><Icon size={28} /></div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <h3 className="text-base font-semibold">{app.label}</h3>
                    <span className="text-xs text-gray-500 shrink-0">{app.size}</span>
                  </div>
                  <p className="text-sm text-gray-400 mt-0.5 mb-3">{app.desc}</p>
                  <a href={app.url} download
                    className="inline-flex items-center gap-1.5 bg-slate-700/50 hover:bg-slate-600/50 text-slate-200 px-4 py-2 rounded-lg text-sm font-medium transition-colors border border-slate-600/50">
                    <Download size={15} />
                    Download
                  </a>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {!publicView && (
        <div className="bg-[#1e2139] rounded-xl border border-[#2a2d3e] p-4">
          <DataTable columns={columns} data={downloads} loading={loading} />
        </div>
      )}
    </div>
  )
}
