import {
  LayoutDashboard,
  BarChart3,
  Package,
  FileText,
  Settings,
  UserCircle,
  X,
} from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { useEffect } from "react";

interface SidebarProps {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
}

export function Sidebar({ isOpen, setIsOpen }: SidebarProps) {
  const location = useLocation();

  // Close sidebar on route change on mobile
  useEffect(() => {
    setIsOpen(false);
  }, [location.pathname, setIsOpen]);

  const navItems = [
    { icon: LayoutDashboard, label: "Dashboard", path: "/app" },
    { icon: BarChart3, label: "Analysis", path: "/app/analysis" },
    { icon: Package, label: "Resources", path: "/app/resources" },
    { icon: FileText, label: "Reports", path: "/app/reports" },
    { icon: Settings, label: "Settings", path: "/app/settings" },
    { icon: UserCircle, label: "Profile", path: "/app/profile" },
  ];

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 md:hidden transition-opacity"
          onClick={() => setIsOpen(false)}
        />
      )}

      <aside
        className={`fixed md:static inset-y-0 left-0 z-50 w-64 bg-white border-r border-slate-200 flex flex-col transition-transform duration-300 ease-in-out ${
          isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-6 border-b border-slate-200 shrink-0">
          <a href="http://localhost:5173/" className="flex items-center gap-2">
            <img
              src="/prism-logo.png"
              alt="PRISM Logo"
              className="h-10 w-auto object-contain"
            />
            <span className="font-serif font-bold text-slate-800 text-xl tracking-tight">
              PRISM
            </span>
          </a>
          <button
            onClick={() => setIsOpen(false)}
            aria-label="Close navigation menu"
            title="Close menu"
            className="md:hidden p-2 -mr-2 text-slate-400 hover:text-slate-800 hover:bg-slate-100 rounded transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 overflow-y-auto">
          <ul className="space-y-1">
            {navItems.map(({ icon: Icon, label, path }) => {
              const isActive = location.pathname === path;
              return (
                <li key={label}>
                  <Link
                    to={path}
                    className={`flex items-center gap-3 px-4 py-3 rounded text-sm font-medium transition-colors border ${
                      isActive
                        ? "bg-terracotta-50 text-terracotta-600 border-terracotta-500/20 shadow-none"
                        : "text-slate-500 hover:text-slate-800 hover:bg-slate-50 border-transparent shadow-none"
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    {label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-slate-200 text-xs text-slate-400 shrink-0">
          v1.0.0 — Mission Control
        </div>
      </aside>
    </>
  );
}
