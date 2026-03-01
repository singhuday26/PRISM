import { useState, useEffect } from "react";
import { BedShortageWidget } from "../components/BedShortageWidget";
import {
  fetchAlerts,
  fetchDiseases,
  type Alert,
  type DiseaseInfo,
} from "../lib/api";
import { AlertTriangle, Plus, Search, Activity } from "lucide-react";
import { useToast } from "../context/ToastContext";
import { Skeleton } from "../components/ui/Skeleton";

export function Resources() {
  const [criticalRegions, setCriticalRegions] = useState<string[]>([]);
  const [customRegionsList, setCustomRegionsList] = useState<string[]>([]);
  const [alertsLoading, setAlertsLoading] = useState(true);
  const [customRegionInput, setCustomRegionInput] = useState("");
  const [disease, setDisease] = useState("DENGUE");
  const [diseases, setDiseases] = useState<DiseaseInfo[]>([]);
  const { error, info } = useToast();

  useEffect(() => {
    fetchDiseases()
      .then((d) => setDiseases(d.diseases))
      .catch((e) => {
        console.error(e);
        error("Failed to load diseases");
      });
  }, [error]);

  useEffect(() => {
    let active = true;
    async function loadCriticalRegions() {
      setAlertsLoading(true);
      try {
        const data = await fetchAlerts(undefined, disease, 50);
        const highRiskRegions = data.alerts
          .filter(
            (alert: Alert) =>
              alert.risk_level === "CRITICAL" || alert.risk_level === "HIGH" ||
              alert.severity === "CRITICAL" || alert.severity === "HIGH",
          )
          .map((alert: Alert) => alert.region_id);

        const uniqueRegions = Array.from(new Set(highRiskRegions)) as string[];
        if (active) {
          setCriticalRegions(uniqueRegions);
          if (uniqueRegions.length === 0) {
            info(`No critical resource shortages for ${disease}`);
          }
        }
      } catch (err) {
        if (active) {
          console.error("Failed to load alerts:", err);
          error("Failed to load critical regions");
        }
      } finally {
        if (active) setAlertsLoading(false);
      }
    }
    loadCriticalRegions();
    return () => { active = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [disease]);

  const addRegion = () => {
    if (customRegionInput) {
      const regionId = customRegionInput.toUpperCase();
      if (!criticalRegions.includes(regionId) && !customRegionsList.includes(regionId)) {
        setCustomRegionsList([...customRegionsList, regionId]);
      }
      setCustomRegionInput("");
    }
  };

  const displayRegions = Array.from(new Set([...criticalRegions, ...customRegionsList]));

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white mb-2">
            Resource Allocation
          </h1>
          <p className="text-gray-400">
            Monitor and predict healthcare resource demands.
          </p>
        </div>
        <div className="flex gap-4 items-center">
          <select
            value={disease}
            onChange={(e) => setDisease(e.target.value)}
            className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40"
          >
            {diseases.map((d) => (
              <option key={d.disease_id} value={d.disease_id} className="bg-gray-900">
                {d.name}
              </option>
            ))}
            {diseases.length === 0 && (
              <option value="DENGUE" className="bg-gray-900">Dengue Fever</option>
            )}
          </select>
        </div>
      </div>

      {/* Add Custom Region */}
      <div className="glass-card p-4 border border-white/5 rounded-xl flex gap-4 items-center focus-within:border-blue-500/50 transition-colors">
        <Search className="w-5 h-5 text-gray-400 ml-2" />
        <input
          type="text"
          placeholder="Monitor Specific Region ID (e.g., IN-MH)..."
          value={customRegionInput}
          onChange={(e) => setCustomRegionInput(e.target.value)}
          className="bg-transparent border-none outline-none text-white flex-1 placeholder:text-gray-500"
          onKeyDown={(e) => e.key === "Enter" && addRegion()}
        />
        <button
          onClick={addRegion}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors font-medium text-sm"
        >
          <Plus className="w-4 h-4" />
          <span className="hidden sm:inline">Add Region</span>
        </button>
      </div>

      {/* Grid of Resource Widgets */}
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <Activity className="w-5 h-5 text-indigo-400" />
          <h2 className="text-lg font-semibold text-white">Critical Shortage Predictions</h2>
        </div>

        {alertsLoading ? (
          <div className="space-y-6">
            <Skeleton className="h-[200px] w-full rounded-xl" />
            <Skeleton className="h-[200px] w-full rounded-xl" />
          </div>
        ) : displayRegions.length > 0 ? (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            {displayRegions.map((regionId) => (
              <div key={regionId} className="relative group">
                <div className="absolute -left-3 top-4 bottom-4 w-1 bg-gradient-to-b from-blue-500/50 to-indigo-500/50 rounded-full opacity-50 group-hover:opacity-100 transition-opacity" />
                <BedShortageWidget
                  regionId={regionId}
                  disease={disease}
                  capacityThreshold={150} // Higher threshold for critical 
                />
              </div>
            ))}
          </div>
        ) : (
          <div className="glass-card p-16 text-center text-gray-500 border border-white/5 rounded-xl border-dashed">
            <div className="w-16 h-16 rounded-full bg-emerald-500/10 flex items-center justify-center mx-auto mb-4">
              <AlertTriangle className="w-8 h-8 text-emerald-400 opacity-80" />
            </div>
            <h3 className="text-lg font-medium text-slate-300 mb-2">No Critical Shortages</h3>
            <p className="max-w-md mx-auto">
              System health is stable. Try adding a custom region ID above to manually monitor its resource capacity.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
