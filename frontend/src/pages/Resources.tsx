import { useState, useEffect } from "react";
import { BedShortageWidget } from "../components/BedShortageWidget";
import {
  fetchAlerts,
  fetchDiseases,
  fetchRegions,
  type Alert,
  type DiseaseInfo,
  type Region,
} from "../lib/api";
import { AlertTriangle, Activity, ChevronDown } from "lucide-react";
import { useToast } from "../context/ToastContext";
import { Skeleton } from "../components/ui/Skeleton";

export function Resources() {
  const [criticalRegions, setCriticalRegions] = useState<string[]>([]);
  const [alertsLoading, setAlertsLoading] = useState(true);
  const [selectedRegion, setSelectedRegion] = useState("");
  const [showAllAlerts, setShowAllAlerts] = useState(true);
  const [disease, setDisease] = useState("DENGUE");
  const [diseases, setDiseases] = useState<DiseaseInfo[]>([]);
  const [allRegions, setAllRegions] = useState<Region[]>([]);
  const [regionsLoading, setRegionsLoading] = useState(true);
  const { error, info } = useToast();

  // Load diseases
  useEffect(() => {
    fetchDiseases()
      .then((d) => setDiseases(d.diseases))
      .catch((e) => {
        console.error(e);
        error("Failed to load diseases");
      });
  }, [error]);

  // Load all available regions for the dropdown
  useEffect(() => {
    setRegionsLoading(true);
    fetchRegions()
      .then((r) => {
        setAllRegions(r.regions);
      })
      .catch((e) => {
        console.error(e);
        error("Failed to load regions list");
      })
      .finally(() => setRegionsLoading(false));
  }, [error]);

  // Load critical regions based on alerts
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
  }, [disease, showAllAlerts]);

  // Build display list: if a region is selected, ONLY show that region.
  // Otherwise, if showAllAlerts is true, show up to 4 critical alerts.
  const displayRegions = selectedRegion 
    ? [selectedRegion.toUpperCase()] 
    : (showAllAlerts ? criticalRegions.slice(0, 4).map(r => r.toUpperCase()) : []);

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-serif font-bold text-slate-800 mb-2">
            Resource Allocation
          </h1>
          <p className="text-slate-500">
            Monitor and predict healthcare resource demands.
          </p>
        </div>
        <div className="flex gap-4 items-center">
          {/* System Alerts Toggle */}
          {!selectedRegion && (
            <label className="flex items-center gap-2 cursor-pointer group">
              <div className="relative">
                <input
                  type="checkbox"
                  checked={showAllAlerts}
                  onChange={(e) => setShowAllAlerts(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-10 h-5 bg-slate-200 rounded-full peer peer-checked:bg-[#E07A5F] transition-colors" />
                <div className="absolute left-1 top-1 w-3 h-3 bg-white peer-checked:translate-x-5 rounded-full shadow-sm transition-all" />
              </div>
              <span className="text-xs text-slate-500 font-medium group-hover:text-slate-700 transition-colors">
                Show System Alerts
              </span>
            </label>
          )}

          {/* Disease Selector */}
          <div className="relative">
            <select
              value={disease}
              onChange={(e) => setDisease(e.target.value)}
              className="appearance-none bg-white border border-slate-200 rounded-lg pl-3 pr-8 py-2 text-sm text-slate-800 font-medium focus:outline-none focus:ring-2 focus:ring-[#E07A5F]/40 cursor-pointer shadow-sm"
            >
              {diseases.map((d) => (
                <option key={d.disease_id} value={d.disease_id}>
                  {d.name}
                </option>
              ))}
              {diseases.length === 0 && (
                <option value="DENGUE">Dengue Fever</option>
              )}
            </select>
            <ChevronDown className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          </div>
        </div>
      </div>

      {/* Region Selector — Direct Filter */}
      <div className="bg-white/60 backdrop-blur-md p-4 border border-slate-200 rounded-xl flex flex-col sm:flex-row gap-3 items-stretch sm:items-center focus-within:border-slate-300 transition-colors shadow-sm">
        <div className="flex-1 relative">
          <select
            value={selectedRegion}
            onChange={(e) => setSelectedRegion(e.target.value)}
            disabled={regionsLoading}
            className="w-full appearance-none bg-white border border-slate-200 rounded-lg pl-4 pr-10 py-2.5 text-sm font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#E07A5F]/40 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
          >
            <option value="" className="text-slate-500">
              {regionsLoading ? "Loading regions…" : "Select a region to focus on…"}
            </option>
            {allRegions.map((r) => (
              <option key={r.region_id} value={r.region_id}>
                {r.region_name} ({r.region_id})
              </option>
            ))}
          </select>
          <ChevronDown className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
        </div>
        {selectedRegion && (
          <button
            onClick={() => setSelectedRegion("")}
            className="px-4 py-2 text-xs font-medium text-slate-600 hover:text-slate-900 transition-colors border border-slate-200 rounded-lg hover:bg-slate-50"
          >
            Clear Selection
          </button>
        )}
      </div>

      {/* Grid of Resource Widgets */}
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <Activity className="w-5 h-5 text-slate-600" />
          <h2 className="text-lg font-serif font-bold text-slate-800">
            {selectedRegion ? "Resource Demands" : "Top Critical Shortage Predictions"}
          </h2>
        </div>

        {alertsLoading ? (
          <div className="space-y-6">
            <Skeleton className="h-[200px] w-full rounded-xl bg-slate-100" />
            <Skeleton className="h-[200px] w-full rounded-xl bg-slate-100" />
          </div>
        ) : displayRegions.length > 0 ? (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            {displayRegions.map((regionId) => {
              const regionInfo = allRegions.find(
                (r) => r.region_id.toUpperCase() === regionId.toUpperCase(),
              );
              return (
                <div key={regionId} className="relative group">
                  <div className="absolute -left-3 top-4 bottom-4 w-1 bg-gradient-to-b from-[#E07A5F] to-slate-200 rounded-full opacity-50 group-hover:opacity-100 transition-opacity" />
                  {regionInfo && (
                    <p className="text-xs font-serif font-medium text-slate-500 pl-1 mb-1">
                      {regionInfo.region_name}
                    </p>
                  )}
                  <BedShortageWidget
                    regionId={regionId}
                    disease={disease}
                    capacityThreshold={150}
                  />
                </div>
              );
            })}
          </div>
        ) : (
          <div className="bg-white/60 backdrop-blur-md p-16 text-center text-slate-500 border border-slate-200 rounded-xl border-dashed shadow-sm">
            <div className="w-16 h-16 rounded-full bg-emerald-50 flex items-center justify-center mx-auto mb-4 border border-emerald-100">
              <AlertTriangle className="w-8 h-8 text-emerald-500 opacity-80" />
            </div>
            <h3 className="text-lg font-serif font-bold text-slate-800 mb-2">No Critical Shortages</h3>
            <p className="max-w-md mx-auto text-sm">
              System health is stable. Use the dropdown above to manually add a region for monitoring.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
