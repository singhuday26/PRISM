import { AlertTriangle, Bell } from "lucide-react";

export function Header() {
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
