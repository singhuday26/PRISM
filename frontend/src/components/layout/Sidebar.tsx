import {
    LayoutDashboard,
    BarChart3,
    Package,
    FileText,
    Settings,
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
                className={`fixed md:static inset-y-0 left-0 z-50 w-64 bg-[hsl(240,10%,5%)] border-r border-white/10 flex flex-col transition-transform duration-300 ease-in-out ${isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
                    }`}
            >
                {/* Logo */}
                <div className="h-16 flex items-center justify-between px-6 border-b border-white/10 shrink-0">
                    <h1 className="text-xl font-bold tracking-tight">
                        <span className="text-blue-400">PRISM</span>
                        <span className="text-gray-400 font-normal ml-2">COMMAND</span>
                    </h1>
                    <button
                        onClick={() => setIsOpen(false)}
                        className="md:hidden p-2 -mr-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
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
                <div className="p-4 border-t border-white/10 text-xs text-gray-500 shrink-0">
                    v1.0.0 — Mission Control
                </div>
            </aside>
        </>
    );
}
