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
import { AlertTriangle, Plus, Activity, ChevronDown } from "lucide-react";
import { useToast } from "../context/ToastContext";
import { Skeleton } from "../components/ui/Skeleton";

export function Resources() {
  const [criticalRegions, setCriticalRegions] = useState<string[]>([]);
  const [customRegionsList, setCustomRegionsList] = useState<string[]>([]);
  const [alertsLoading, setAlertsLoading] = useState(true);
  const [selectedRegion, setSelectedRegion] = useState("");
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
  }, [disease]);

  const addRegion = () => {
    if (selectedRegion) {
      const regionId = selectedRegion.toUpperCase();
      if (!criticalRegions.includes(regionId) && !customRegionsList.includes(regionId)) {
        setCustomRegionsList([...customRegionsList, regionId]);
      }
      setSelectedRegion("");
    }
  };

  const removeCustomRegion = (regionId: string) => {
    setCustomRegionsList(customRegionsList.filter((r) => r !== regionId));
  };

  const displayRegions = Array.from(new Set([...criticalRegions, ...customRegionsList]));

  // Build set of already-monitored region IDs
  const monitoredSet = new Set(displayRegions.map((r) => r.toUpperCase()));

  // Regions available in dropdown = all regions not already monitored
  const availableRegions = allRegions.filter(
    (r) => !monitoredSet.has(r.region_id.toUpperCase()),
  );

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
          {/* Disease Selector */}
          <div className="relative">
            <select
              value={disease}
              onChange={(e) => setDisease(e.target.value)}
              className="appearance-none bg-white/5 border border-white/10 rounded-lg pl-3 pr-8 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40 cursor-pointer"
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
            <ChevronDown className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>
        </div>
      </div>

      {/* Add Custom Region — Dropdown */}
      <div className="glass-card p-4 border border-white/5 rounded-xl flex flex-col sm:flex-row gap-3 items-stretch sm:items-center focus-within:border-blue-500/50 transition-colors">
        <div className="flex-1 relative">
          <select
            value={selectedRegion}
            onChange={(e) => setSelectedRegion(e.target.value)}
            disabled={regionsLoading}
            className="w-full appearance-none bg-white/5 border border-white/10 rounded-lg pl-4 pr-10 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <option value="" className="bg-gray-900 text-gray-400">
              {regionsLoading ? "Loading regions…" : "Select a region to monitor…"}
            </option>
            {availableRegions.map((r) => (
              <option key={r.region_id} value={r.region_id} className="bg-gray-900">
                {r.region_name} ({r.region_id})
              </option>
            ))}
            {!regionsLoading && availableRegions.length === 0 && allRegions.length > 0 && (
              <option disabled className="bg-gray-900 text-gray-500">
                All regions are already being monitored
              </option>
            )}
          </select>
          <ChevronDown className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        </div>
        <button
          onClick={addRegion}
          disabled={!selectedRegion}
          className="flex items-center justify-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-lg transition-colors font-medium text-sm"
        >
          <Plus className="w-4 h-4" />
          <span>Add Region</span>
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
            {displayRegions.map((regionId) => {
              const regionInfo = allRegions.find(
                (r) => r.region_id.toUpperCase() === regionId.toUpperCase(),
              );
              const isCustom = customRegionsList.includes(regionId);
              return (
                <div key={regionId} className="relative group">
                  <div className="absolute -left-3 top-4 bottom-4 w-1 bg-gradient-to-b from-blue-500/50 to-indigo-500/50 rounded-full opacity-50 group-hover:opacity-100 transition-opacity" />
                  {isCustom && (
                    <button
                      onClick={() => removeCustomRegion(regionId)}
                      className="absolute top-3 right-3 z-10 text-xs text-gray-500 hover:text-red-400 transition-colors bg-white/5 hover:bg-red-500/10 rounded px-2 py-0.5 border border-white/10"
                    >
                      Remove
                    </button>
                  )}
                  {regionInfo && (
                    <p className="text-xs text-gray-500 pl-1 mb-1">
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
          <div className="glass-card p-16 text-center text-gray-500 border border-white/5 rounded-xl border-dashed">
            <div className="w-16 h-16 rounded-full bg-emerald-500/10 flex items-center justify-center mx-auto mb-4">
              <AlertTriangle className="w-8 h-8 text-emerald-400 opacity-80" />
            </div>
            <h3 className="text-lg font-medium text-slate-300 mb-2">No Critical Shortages</h3>
            <p className="max-w-md mx-auto">
              System health is stable. Use the dropdown above to manually add a region for monitoring.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
