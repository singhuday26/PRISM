import { useState, useEffect } from "react";
import { AlertTriangle, Bell, CheckCircle, LogOut, Menu, UserCircle } from "lucide-react";
import { fetchAlerts, type Alert } from "../../lib/api";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router-dom";

const SEVERITY_STYLES: Record<
  string,
  { bg: string; border: string; text: string; icon: string }
> = {
  CRITICAL: {
    bg: "bg-terracotta-50",
    border: "border-terracotta-500",
    text: "text-terracotta-600",
    icon: "text-terracotta-600",
  },
  HIGH: {
    bg: "bg-terracotta-50",
    border: "border-terracotta-500/50",
    text: "text-terracotta-600",
    icon: "text-terracotta-600",
  },
  MEDIUM: {
    bg: "bg-slate-50",
    border: "border-slate-200",
    text: "text-slate-800",
    icon: "text-slate-800",
  },
  LOW: {
    bg: "bg-slate-50",
    border: "border-slate-200",
    text: "text-slate-500",
    icon: "text-slate-500",
  },
};

export function Header({ onMenuClick }: { onMenuClick: () => void }) {
  const [latestAlert, setLatestAlert] = useState<Alert | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [alertCount, setAlertCount] = useState(0);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

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
    <header className="h-16 shrink-0 bg-white/80 backdrop-blur-md border-b border-slate-200 flex items-center justify-between px-4 sm:px-6 z-40 relative">
      <div className="flex items-center gap-3 w-full sm:w-auto overflow-hidden">
        <button
          onClick={onMenuClick}
          className="md:hidden p-2 -ml-2 text-slate-400 hover:text-slate-800 hover:bg-slate-100 rounded transition-colors shrink-0"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div className="md:hidden flex items-center gap-2">
            <img 
            src="/prism-logo.png" 
            alt="PRISM Logo" 
            className="h-9 w-auto object-contain"
            />
            <span className="font-serif font-bold text-slate-800 text-lg tracking-tight">PRISM</span>
        </div>
        {/* Alert Banner */}
        {latestAlert && style ? (
          <div
            className={`flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-1.5 sm:py-2 rounded ${style.bg} border ${style.border} truncate`}
          >
            <AlertTriangle className={`w-4 h-4 shrink-0 ${style.icon}`} />
            <span className={`text-xs sm:text-sm ${style.text} font-medium tracking-tight truncate`}>
              {latestAlert.risk_level || latestAlert.severity || "MEDIUM"}:{" "}
              {latestAlert.reason ||
                `Alert in ${latestAlert.region_id}`}
            </span>
          </div>
        ) : (
          <div className="flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-1.5 sm:py-2 rounded bg-slate-50 border border-slate-200 truncate">
            <CheckCircle className="w-4 h-4 shrink-0 text-slate-500" />
            <span className="text-xs sm:text-sm text-slate-600 font-medium tracking-tight truncate">
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
            className={`p-2 rounded transition-colors relative hidden sm:block ${isNotificationsOpen ? 'bg-slate-100 text-slate-800' : 'hover:bg-slate-50 text-slate-500 hover:text-slate-800'}`}
            title={`${alertCount} recent alerts`}
          >
            <Bell className="w-5 h-5" />
            {alertCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 bg-terracotta-500 rounded-full text-[10px] font-bold text-white flex items-center justify-center">
                {alertCount > 99 ? "99+" : alertCount}
              </span>
            )}
          </button>

          {isNotificationsOpen && (
            <div className="absolute top-full right-0 mt-2 w-80 bg-white border border-slate-200 rounded shadow-sm overflow-hidden z-[60]">
              <div className="p-3 border-b border-slate-200 font-serif font-semibold text-slate-800">Notifications</div>
              <div className="max-h-96 overflow-y-auto">
                {alerts.length > 0 ? (
                  alerts.map((alert, i) => (
                    <div key={i} className="p-3 border-b border-slate-100 hover:bg-slate-50 transition-colors">
                      <div className="text-sm font-medium text-slate-800">{alert.severity || alert.risk_level} Alert</div>
                      <div className="text-xs text-slate-500 mt-1">{alert.reason || `${alert.disease || 'Alert'} in ${alert.region_id}`}</div>
                    </div>
                  ))
                ) : (
                  <div className="p-4 text-center text-sm text-slate-400">No new notifications</div>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="relative border-l border-slate-200 pl-2 sm:pl-4">
          <button
            onClick={() => { setIsProfileOpen(!isProfileOpen); setIsNotificationsOpen(false); }}
            className={`flex items-center gap-2 sm:gap-3 p-1 rounded transition-colors ${isProfileOpen ? 'bg-slate-50' : 'hover:bg-slate-50'}`}
          >
            <div className="hidden sm:flex flex-col items-end mr-1 text-left">
              <span className="text-sm text-slate-800 font-serif font-medium">{user?.username || "User"}</span>
              <span className="text-[10px] text-slate-500 uppercase tracking-widest">{user?.role || "Viewer"}</span>
            </div>
            <div className="w-7 h-7 sm:w-8 sm:h-8 shrink-0 rounded bg-slate-100 flex items-center justify-center text-xs sm:text-sm font-bold text-slate-600 border border-slate-200">
              {user?.username?.[0].toUpperCase() || "U"}
            </div>
          </button>

          {isProfileOpen && (
            <div className="absolute top-full right-0 mt-2 w-52 bg-white border border-slate-200 rounded shadow-sm overflow-hidden z-[60]">
              <div className="px-4 py-2 text-xs text-slate-400 uppercase tracking-wider border-b border-slate-100 mb-1">
                Account
              </div>
              <button
                onClick={() => { setIsProfileOpen(false); navigate("/app/profile"); }}
                className="w-full text-left px-4 py-2.5 text-sm text-slate-600 hover:bg-slate-50 hover:text-slate-800 flex items-center gap-2 transition-colors"
              >
                <UserCircle className="w-4 h-4 text-slate-400" />
                My Profile
              </button>
              <button
                onClick={logout}
                className="w-full text-left px-4 py-2.5 text-sm text-terracotta-600 hover:bg-terracotta-50 flex items-center gap-2 transition-colors"
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
