import { LucideIcon } from 'lucide-react'

interface StatCardProps {
  title: string
  value: string | number
  icon: LucideIcon
  color?: string
}

export default function StatCard({ title, value, icon: Icon, color = 'text-indigo-400' }: StatCardProps) {
  return (
    <div className="bg-[#1e2139] rounded-xl p-5 border border-[#2a2d3e]">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className={`p-3 rounded-lg bg-indigo-600/10 ${color}`}>
          <Icon size={24} />
        </div>
      </div>
    </div>
  )
}
