import { useState, useEffect } from "react";
import { AlertTriangle, Bell, CheckCircle, LogOut, Menu } from "lucide-react";
import { fetchAlerts, type Alert } from "../../lib/api";
import { useAuth } from "../../context/AuthContext";

const SEVERITY_STYLES: Record<
  string,
  { bg: string; border: string; text: string; icon: string }
> = {
  CRITICAL: {
    bg: "bg-red-500/10",
    border: "border-red-500/30",
    text: "text-red-400",
    icon: "text-red-400",
  },
  HIGH: {
    bg: "bg-orange-500/10",
    border: "border-orange-500/30",
    text: "text-orange-400",
    icon: "text-orange-400",
  },
  MEDIUM: {
    bg: "bg-yellow-500/10",
    border: "border-yellow-500/30",
    text: "text-yellow-400",
    icon: "text-yellow-400",
  },
  LOW: {
    bg: "bg-blue-500/10",
    border: "border-blue-500/30",
    text: "text-blue-400",
    icon: "text-blue-400",
  },
};

export function Header({ onMenuClick }: { onMenuClick: () => void }) {
  const [latestAlert, setLatestAlert] = useState<Alert | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [alertCount, setAlertCount] = useState(0);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const { user, logout } = useAuth();

  useEffect(() => {
    fetchAlerts(undefined, undefined, 5)
      .then((data) => {
        setAlertCount(data.count);
        if (data.alerts) {
          setAlerts(data.alerts);
          if (data.alerts.length > 0) setLatestAlert(data.alerts[0]);
        }
      })
      .catch((e) => console.error("Failed to fetch alerts for header", e));
  }, []);

  const style = latestAlert
    ? (SEVERITY_STYLES[latestAlert.risk_level || latestAlert.severity || "MEDIUM"] ?? SEVERITY_STYLES.MEDIUM)
    : null;

  return (
    <header className="h-16 shrink-0 bg-[hsl(240,10%,5%)] border-b border-white/10 flex items-center justify-between px-4 sm:px-6">
      <div className="flex items-center gap-3 w-full sm:w-auto overflow-hidden">
        <button
          onClick={onMenuClick}
          className="md:hidden p-2 -ml-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors shrink-0"
        >
          <Menu className="w-5 h-5" />
        </button>
        {/* Alert Banner */}
        {latestAlert && style ? (
          <div
            className={`flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg ${style.bg} border ${style.border} truncate`}
          >
            <AlertTriangle className={`w-4 h-4 shrink-0 ${style.icon}`} />
            <span className={`text-xs sm:text-sm ${style.text} font-medium truncate`}>
              {latestAlert.severity}:{" "}
              {latestAlert.reason ||
                `Alert in ${latestAlert.region_id}`}
            </span>
          </div>
        ) : (
          <div className="flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg bg-green-500/10 border border-green-500/30 truncate">
            <CheckCircle className="w-4 h-4 shrink-0 text-green-400" />
            <span className="text-xs sm:text-sm text-green-400 font-medium truncate">
              All systems nominal
            </span>
          </div>
        )}
      </div>

      {/* User Menu & Notifications */}
      <div className="flex items-center gap-2 sm:gap-4 shrink-0 ml-2 relative">
        <div className="relative">
          <button
            onClick={() => { setIsNotificationsOpen(!isNotificationsOpen); setIsProfileOpen(false); }}
            className={`p-2 rounded-lg transition-colors relative hidden sm:block ${isNotificationsOpen ? 'bg-white/10 text-white' : 'hover:bg-white/5 text-gray-400 hover:text-white'}`}
            title={`${alertCount} recent alerts`}
          >
            <Bell className="w-5 h-5" />
            {alertCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 bg-red-500 rounded-full text-[10px] font-bold text-white flex items-center justify-center">
                {alertCount > 99 ? "99+" : alertCount}
              </span>
            )}
          </button>

          {isNotificationsOpen && (
            <div className="absolute top-full right-0 mt-2 w-80 bg-[hsl(240,10%,10%)] border border-white/10 rounded-lg shadow-xl overflow-hidden z-50">
              <div className="p-3 border-b border-white/10 font-semibold text-white">Notifications</div>
              <div className="max-h-96 overflow-y-auto">
                {alerts.length > 0 ? (
                  alerts.map((alert, i) => (
                    <div key={i} className="p-3 border-b border-white/5 hover:bg-white/5 transition-colors">
                      <div className="text-sm font-medium text-white">{alert.severity || alert.risk_level} Alert</div>
                      <div className="text-xs text-gray-400 mt-1">{alert.reason || `${alert.disease || 'Alert'} in ${alert.region_id}`}</div>
                    </div>
                  ))
                ) : (
                  <div className="p-4 text-center text-sm text-gray-500">No new notifications</div>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="relative border-l border-white/10 pl-2 sm:pl-4">
          <button
            onClick={() => { setIsProfileOpen(!isProfileOpen); setIsNotificationsOpen(false); }}
            className={`flex items-center gap-2 sm:gap-3 p-1 rounded-lg transition-colors ${isProfileOpen ? 'bg-white/5' : 'hover:bg-white/5'}`}
          >
            <div className="hidden sm:flex flex-col items-end mr-1 text-left">
              <span className="text-sm text-gray-300 font-medium">{user?.username || "User"}</span>
              <span className="text-[10px] text-gray-500 uppercase tracking-widest">{user?.role || "Viewer"}</span>
            </div>
            <div className="w-7 h-7 sm:w-8 sm:h-8 shrink-0 rounded-full bg-blue-500/20 flex items-center justify-center text-xs sm:text-sm font-bold text-blue-400 ring-1 ring-blue-500/30">
              {user?.username?.[0].toUpperCase() || "U"}
            </div>
          </button>

          {isProfileOpen && (
            <div className="absolute top-full right-0 mt-2 w-48 bg-[hsl(240,10%,10%)] border border-white/10 rounded-lg shadow-xl overflow-hidden z-50 py-1">
              <div className="px-4 py-2 text-xs text-gray-400 uppercase tracking-wider border-b border-white/10 mb-1">
                Account
              </div>
              <button
                onClick={logout}
                className="w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-red-500/10 flex items-center gap-2 transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
