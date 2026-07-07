import { LogOut, User } from 'lucide-react'

interface HeaderProps {
  user: { name: string; email: string }
  onLogout: () => void
}

export default function Header({ user, onLogout }: HeaderProps) {
  return (
    <header className="h-16 border-b border-[#2a2d3e] bg-[#1a1d2e] flex items-center justify-between px-6">
      <div className="text-sm text-gray-400">Welcome back, <span className="text-white font-medium">{user.name}</span></div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <User size={16} />
          {user.email}
        </div>
        <button
          onClick={onLogout}
          className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-400 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-colors"
        >
          <LogOut size={16} />
          Logout
        </button>
      </div>
    </header>
  )
}
