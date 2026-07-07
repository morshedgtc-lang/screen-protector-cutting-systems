import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Users, Printer, Blocks, FileType, Tag,
  ListChecks, CreditCard, Settings, Download, RefreshCw, ScrollText,
} from 'lucide-react'

const links = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/users', label: 'Users', icon: Users },
  { to: '/machines', label: 'Machines', icon: Printer },
  { to: '/machine-types', label: 'Machine Types', icon: Blocks },
  { to: '/jobs', label: 'Jobs', icon: ListChecks },
  { to: '/templates', label: 'Templates', icon: FileType },
  { to: '/brands', label: 'Brands & Models', icon: Tag },
  { to: '/subscriptions', label: 'Subscriptions', icon: CreditCard },
  { to: '/logs', label: 'Logs', icon: ScrollText },
  { to: '/updates', label: 'Updates', icon: RefreshCw },
  { to: '/downloads', label: 'Downloads', icon: Download },
  { to: '/settings', label: 'Settings', icon: Settings },
]

interface SidebarProps {
  user: { name: string; role: string }
}

export default function Sidebar({ user }: SidebarProps) {
  return (
    <aside className="w-64 bg-[#1a1d2e] border-r border-[#2a2d3e] flex flex-col">
      <div className="p-5 border-b border-[#2a2d3e]">
        <h1 className="text-lg font-bold text-indigo-400">SATelecom CutOS</h1>
        <p className="text-xs text-gray-500 mt-1 capitalize">{user.role}</p>
      </div>
      <nav className="flex-1 overflow-y-auto p-3 space-y-1">
        {links.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            end={l.to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'bg-indigo-600/20 text-indigo-400'
                  : 'text-gray-400 hover:text-white hover:bg-[#2a2d3e]'
              }`
            }
          >
            <l.icon size={18} />
            {l.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
