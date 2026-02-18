import { useState, useEffect } from "react";
import { AlertTriangle, Bell, CheckCircle } from "lucide-react";
import { fetchAlerts, type Alert } from "../../lib/api";

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

export function Header() {
  const [latestAlert, setLatestAlert] = useState<Alert | null>(null);
  const [alertCount, setAlertCount] = useState(0);

  useEffect(() => {
    fetchAlerts(undefined, undefined, 5)
      .then((data) => {
        setAlertCount(data.count);
        if (data.alerts && data.alerts.length > 0) {
          setLatestAlert(data.alerts[0]);
        }
      })
      .catch((e) => console.error("Failed to fetch alerts for header", e));
  }, []);

  const style = latestAlert
    ? (SEVERITY_STYLES[latestAlert.severity] ?? SEVERITY_STYLES.MEDIUM)
    : null;

  return (
    <header className="h-16 bg-[hsl(240,10%,5%)] border-b border-white/10 flex items-center justify-between px-6">
      {/* Alert Banner */}
      {latestAlert && style ? (
        <div
          className={`flex items-center gap-3 px-4 py-2 rounded-lg ${style.bg} border ${style.border}`}
        >
          <AlertTriangle className={`w-4 h-4 ${style.icon}`} />
          <span className={`text-sm ${style.text} font-medium`}>
            {latestAlert.severity}:{" "}
            {latestAlert.reason ||
              `${latestAlert.alert_type} in ${latestAlert.region_id}`}
          </span>
        </div>
      ) : (
        <div className="flex items-center gap-3 px-4 py-2 rounded-lg bg-green-500/10 border border-green-500/30">
          <CheckCircle className="w-4 h-4 text-green-400" />
          <span className="text-sm text-green-400 font-medium">
            All systems nominal
          </span>
        </div>
      )}

      {/* User Menu */}
      <div className="flex items-center gap-4">
        <button
          className="p-2 rounded-lg hover:bg-white/5 transition-colors relative"
          title={`${alertCount} recent alerts`}
        >
          <Bell className="w-5 h-5 text-gray-400" />
          {alertCount > 0 && (
            <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 bg-red-500 rounded-full text-[10px] font-bold text-white flex items-center justify-center">
              {alertCount > 99 ? "99+" : alertCount}
            </span>
          )}
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
