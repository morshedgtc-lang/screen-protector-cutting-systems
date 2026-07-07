export default function SettingsPage({ token }: { token: string }) {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-1">Settings</h2>
      <p className="text-sm text-gray-500 mb-6">System configuration</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-[#1e2139] rounded-xl border border-[#2a2d3e] p-5">
          <h3 className="text-sm font-medium mb-4">General</h3>
          <div className="space-y-4">
            {[
              { label: 'Language', desc: 'System language', value: 'English' },
              { label: 'Timezone', desc: 'Server timezone', value: 'UTC' },
              { label: 'Log Level', desc: 'Application log level', value: 'INFO' },
            ].map((s) => (
              <div key={s.label} className="flex items-center justify-between py-2 border-b border-[#2a2d3e] last:border-0">
                <div>
                  <p className="text-sm">{s.label}</p>
                  <p className="text-xs text-gray-500">{s.desc}</p>
                </div>
                <span className="text-sm text-gray-400">{s.value}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-[#1e2139] rounded-xl border border-[#2a2d3e] p-5">
          <h3 className="text-sm font-medium mb-4">Printing Defaults</h3>
          <div className="space-y-4">
            {[
              { label: 'Auto-advance', desc: 'Auto-advance after cut', value: 'Enabled' },
              { label: 'Cut Speed', desc: 'Default cut speed', value: '300 mm/s' },
              { label: 'Cut Force', desc: 'Default cut force', value: '180 g' },
              { label: 'Blade Offset', desc: 'Default blade compensation', value: '0.3 mm' },
            ].map((s) => (
              <div key={s.label} className="flex items-center justify-between py-2 border-b border-[#2a2d3e] last:border-0">
                <div>
                  <p className="text-sm">{s.label}</p>
                  <p className="text-xs text-gray-500">{s.desc}</p>
                </div>
                <span className="text-sm text-gray-400">{s.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
