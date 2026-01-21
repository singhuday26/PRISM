import {
  LayoutDashboard,
  BarChart3,
  Package,
  FileText,
  Settings,
  AlertTriangle,
  Bell
} from 'lucide-react';
import { BedShortageWidget } from './components/BedShortageWidget';

function Sidebar() {
  const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', active: true },
    { icon: BarChart3, label: 'Analysis', active: false },
    { icon: Package, label: 'Resources', active: false },
    { icon: FileText, label: 'Reports', active: false },
    { icon: Settings, label: 'Settings', active: false },
  ];

  return (
    <aside className="w-64 bg-[hsl(240,10%,5%)] border-r border-white/10 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-white/10">
        <h1 className="text-xl font-bold tracking-tight">
          <span className="text-blue-400">PRISM</span>
          <span className="text-gray-400 font-normal ml-2">COMMAND</span>
        </h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-1">
          {navItems.map(({ icon: Icon, label, active }) => (
            <li key={label}>
              <a
                href="#"
                className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${active
                    ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                  }`}
              >
                <Icon className="w-5 h-5" />
                {label}
              </a>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-white/10 text-xs text-gray-500">
        v1.0.0 — Mission Control
      </div>
    </aside>
  );
}

function Header() {
  return (
    <header className="h-16 bg-[hsl(240,10%,5%)] border-b border-white/10 flex items-center justify-between px-6">
      {/* Alert Banner */}
      <div className="flex items-center gap-3 px-4 py-2 rounded-lg bg-red-500/10 border border-red-500/30">
        <AlertTriangle className="w-4 h-4 text-red-400" />
        <span className="text-sm text-red-400 font-medium">
          ALERT: Resource shortage predicted in Zone 4
        </span>
      </div>

      {/* User Menu */}
      <div className="flex items-center gap-4">
        <button className="p-2 rounded-lg hover:bg-white/5 transition-colors relative">
          <Bell className="w-5 h-5 text-gray-400" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
        </button>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-sm font-medium text-blue-400">
            A
          </div>
          <span className="text-sm text-gray-300">Admin</span>
        </div>
      </div>
    </header>
  );
}

function App() {
  return (
    <div className="flex min-h-screen w-full">
      <Sidebar />

      <div className="flex-1 flex flex-col">
        <Header />

        <main className="flex-1 p-6 overflow-auto">
          {/* Page Title */}
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-white mb-2">
              Mission Control
            </h1>
            <p className="text-gray-400">
              Real-time resource allocation and outbreak monitoring
            </p>
          </div>

          {/* Critical Metrics Section */}
          <section className="mb-8">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-4">
              Critical Metrics
            </h2>
            <BedShortageWidget
              regionId="IN-MH"
              disease="dengue"
              capacityThreshold={100}
            />
          </section>

          {/* Placeholder for Map */}
          <section>
            <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-4">
              Operational Map
            </h2>
            <div className="glass-card h-[400px] flex items-center justify-center text-gray-500">
              <div className="text-center">
                <Package className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>Map visualization coming soon</p>
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}

export default App;
