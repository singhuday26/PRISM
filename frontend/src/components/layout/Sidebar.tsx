import {
    LayoutDashboard,
    BarChart3,
    Package,
    FileText,
    Settings,
} from "lucide-react";
import { Link, useLocation } from "react-router-dom";

export function Sidebar() {
    const location = useLocation();

    const navItems = [
        { icon: LayoutDashboard, label: "Dashboard", path: "/app" },
        { icon: BarChart3, label: "Analysis", path: "/app/analysis" },
        { icon: Package, label: "Resources", path: "/app/resources" },
        { icon: FileText, label: "Reports", path: "/app/reports" },
        { icon: Settings, label: "Settings", path: "/app/settings" },
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
                    {navItems.map(({ icon: Icon, label, path }) => {
                        const isActive = location.pathname === path;
                        return (
                            <li key={label}>
                                <Link
                                    to={path}
                                    className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${isActive
                                        ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                                        : "text-gray-400 hover:text-white hover:bg-white/5"
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
            <div className="p-4 border-t border-white/10 text-xs text-gray-500">
                v1.0.0 — Mission Control
            </div>
        </aside>
    );
}
