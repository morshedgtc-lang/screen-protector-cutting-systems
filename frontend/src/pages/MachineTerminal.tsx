import { useState, useEffect, useRef, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'

const API_BASE = '' 

type MachineStatus = 'disconnected' | 'connected' | 'printing' | 'paused' | 'idle'
type JobProgress = { status: string; progress: number; current_file?: string }

export default function MachineTerminal() {
  const [params] = useSearchParams()
  const [serverUrl, setServerUrl] = useState(params.get('server') || 'http://192.168.0.100:8000')
  const [editingServer, setEditingServer] = useState(false)
  const [serverInput, setServerInput] = useState(serverUrl)
  const [status, setStatus] = useState<MachineStatus>('disconnected')
  const [job, setJob] = useState<JobProgress | null>(null)
  const [message, setMessage] = useState('')
  const wsRef = useRef<WebSocket | null>(null)

  const connectWs = useCallback(() => {
    const wsUrl = serverUrl.replace(/^http/, 'ws') + '/ws/machine/terminal'
    const ws = new WebSocket(wsUrl)
    ws.onopen = () => { setStatus('connected'); setMessage('') }
    ws.onclose = () => { setStatus('disconnected'); setMessage('Disconnected'); setTimeout(connectWs, 3000) }
    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)
        if (data.status) setStatus(data.status)
        if (data.job) setJob(data.job)
        if (data.message) setMessage(data.message)
      } catch { /* ignore */ }
    }
    wsRef.current = ws
  }, [serverUrl])

  useEffect(() => { connectWs(); return () => wsRef.current?.close() }, [connectWs])

  const sendCmd = async (cmd: string) => {
    try {
      const r = await fetch(`${serverUrl}/api/v1/machine/command`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: cmd }),
      })
      if (!r.ok) setMessage(`Command failed: ${r.status}`)
    } catch (e: any) {
      setMessage(`Error: ${e.message}`)
    }
  }

  const statusColor: Record<MachineStatus, string> = {
    disconnected: 'bg-red-500', connected: 'bg-green-500',
    printing: 'bg-blue-500', paused: 'bg-yellow-500', idle: 'bg-green-400',
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col">
      {/* Header */}
      <header className="bg-slate-900 px-4 py-3 flex items-center justify-between border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${statusColor[status]} animate-pulse`} />
          <span className="font-semibold text-lg">CutOS Terminal</span>
          <span className="text-sm text-slate-400 capitalize">{status}</span>
        </div>
        <button onClick={() => { setEditingServer(!editingServer); setServerInput(serverUrl) }}
          className="text-xs text-slate-400 hover:text-white px-3 py-1 rounded bg-slate-800">
          {editingServer ? 'Done' : 'Server'}
        </button>
      </header>

      {/* Server URL editor */}
      {editingServer && (
        <div className="bg-slate-900 px-4 py-3 flex gap-2 items-center border-b border-slate-800">
          <input value={serverInput} onChange={(e) => setServerInput(e.target.value)}
            className="flex-1 bg-slate-800 text-white px-3 py-2 rounded text-sm font-mono" />
          <button onClick={() => { setServerUrl(serverInput); setEditingServer(false); wsRef.current?.close() }}
            className="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium">Connect</button>
        </div>
      )}

      {/* Message */}
      {message && (
        <div className="bg-slate-900 mx-4 mt-3 px-4 py-2 rounded-lg text-sm text-slate-300 border border-slate-800">
          {message}
        </div>
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col p-4 gap-4">
        {/* Job progress */}
        {job && (
          <div className="bg-slate-900 rounded-xl p-5 border border-slate-800">
            <div className="text-sm text-slate-400 mb-1">Current Job</div>
            <div className="text-lg font-semibold mb-2 truncate">{job.current_file || 'N/A'}</div>
            <div className="w-full bg-slate-800 rounded-full h-4 overflow-hidden">
              <div className="bg-blue-500 h-full transition-all duration-300 rounded-full"
                style={{ width: `${job.progress}%` }} />
            </div>
            <div className="text-right text-sm text-slate-400 mt-1">{job.progress}%</div>
          </div>
        )}

        {/* Big control buttons */}
        <div className="grid grid-cols-2 gap-4 flex-1">
          <button onClick={() => sendCmd('start')}
            className="bg-green-600 hover:bg-green-500 rounded-2xl text-2xl font-bold flex items-center justify-center
              active:scale-95 transition-transform disabled:opacity-40"
            disabled={status === 'printing'}>
            START
          </button>
          <button onClick={() => sendCmd('pause')}
            className="bg-yellow-600 hover:bg-yellow-500 rounded-2xl text-2xl font-bold flex items-center justify-center
              active:scale-95 transition-transform disabled:opacity-40"
            disabled={status !== 'printing'}>
            PAUSE
          </button>
          <button onClick={() => sendCmd('resume')}
            className="bg-blue-600 hover:bg-blue-500 rounded-2xl text-2xl font-bold flex items-center justify-center
              active:scale-95 transition-transform disabled:opacity-40"
            disabled={status !== 'paused'}>
            RESUME
          </button>
          <button onClick={() => sendCmd('stop')}
            className="bg-red-600 hover:bg-red-500 rounded-2xl text-2xl font-bold flex items-center justify-center
              active:scale-95 transition-transform disabled:opacity-40">
            STOP
          </button>
        </div>
      </div>

      {/* Bottom indicator */}
      <footer className="bg-slate-900 px-4 py-2 text-center text-xs text-slate-500 border-t border-slate-800">
        SATelecom CutOS v1.0 &mdash; {serverUrl}
      </footer>
    </div>
  )
}
