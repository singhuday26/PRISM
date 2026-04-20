import { Suspense, lazy, useState, useEffect, useCallback } from "react";
import { BedShortageWidget } from "../components/BedShortageWidget";
import {
  fetchRegions,
  fetchDiseases,
  fetchAlerts,
  fetchEvaluationSummary,
  type Region,
  type DiseaseInfo,
} from "../lib/api";
import EarlyWarningFeed from "../components/EarlyWarningFeed";
import PipelineExecutionPanel from "../components/PipelineExecutionPanel";
import { AlertTriangle, MapPin, Activity, BarChart2 } from "lucide-react";

const OperationalMap = lazy(() =>
  import("../components/OperationalMap").then((m) => ({
    default: m.OperationalMap,
  })),
);

function MapLoading() {
  return (
    <div className="h-[500px] bg-white/60 backdrop-blur-md flex items-center justify-center border border-slate-200 rounded-lg">
      <div className="text-center">
        <div className="animate-spin w-8 h-8 border-4 border-slate-400 border-t-transparent rounded-full mx-auto mb-4"></div>
        <p className="text-slate-500 text-sm">Loading map component...</p>
      </div>
    </div>
  );
}

interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  subtext?: string;
  color: string;
}

function MetricCard({ icon, label, value, subtext, color }: MetricCardProps) {
  return (
    <div className="bg-white/60 backdrop-blur-md border border-slate-200 rounded-xl p-5 hover:border-slate-300 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div className={`p-2.5 rounded-lg ${color}`}>{icon}</div>
      </div>
      <div className="text-2xl font-serif font-bold text-slate-800 mb-1">{value}</div>
      <div className="text-xs text-slate-500 uppercase tracking-wider font-medium">
        {label}
      </div>
      {subtext && <div className="text-xs text-slate-400 mt-1">{subtext}</div>}
    </div>
  );
}

export function Dashboard() {
  const [regionId, setRegionId] = useState("IN-MH");
  const [disease, setDisease] = useState("DENGUE");
  const [regions, setRegions] = useState<Region[]>([]);
  const [regionError, setRegionError] = useState<string | null>(null);
  const [diseases, setDiseases] = useState<DiseaseInfo[]>([]);

  // Metrics state
  const [alertCount, setAlertCount] = useState(0);
  const [regionsCount, setRegionsCount] = useState(0);
  const [avgMape, setAvgMape] = useState<number | null>(null);

  const loadMetrics = useCallback(async () => {
    try {
      const [alertsData, regionsData, evalData] = await Promise.allSettled([
        fetchAlerts(undefined, disease, 100),
        fetchRegions(),
        fetchEvaluationSummary(disease),
      ]);

      if (alertsData.status === "fulfilled")
        setAlertCount(alertsData.value?.count ?? 0);
      
      if (regionsData.status === "fulfilled") {
        setRegionsCount(regionsData.value?.count ?? 0);
        setRegions(regionsData.value && Array.isArray(regionsData.value.regions) ? regionsData.value.regions : []);
        setRegionError(null);
      } else {
        const reason = regionsData.reason;
        const message =
          reason instanceof Error ? reason.message : String(reason);
        setRegionError(`Failed to load the regions list: ${message}`);
        console.error("Failed to load the regions list", reason);
      }
      
      if (
        evalData.status === "fulfilled" &&
        evalData.value?.aggregate_mape != null
      ) {
        setAvgMape(evalData.value.aggregate_mape);
      }
    } catch (e) {
      console.error("Failed to load metrics", e);
    }
  }, [disease]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadMetrics();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [loadMetrics]);

  useEffect(() => {
    let active = true;
    fetchDiseases()
      .then((d) => {
        if (active) {
          setDiseases(d && Array.isArray(d.diseases) ? d.diseases : []);
        }
      })
      .catch((e) => console.error("Failed to load diseases", e));

    return () => {
      active = false;
    };
  }, []);

  // Auto-refresh every 60s
  useEffect(() => {
    const interval = window.setInterval(() => {
      void loadMetrics();
    }, 60000);
    return () => clearInterval(interval);
  }, [loadMetrics]);

  return (
    <div className="space-y-8">
      {/* Page Title + Selectors + Pipeline */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-serif font-bold text-slate-800 mb-2">
            Mission Control
          </h1>
          <p className="text-slate-500">
            Real-time resource allocation and outbreak monitoring
          </p>
        </div>
        <div className="flex gap-3 items-center">
          <select
            value={regionId}
            onChange={(e) => setRegionId(e.target.value)}
            aria-label="Select region"
            className="bg-white border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-300"
          >
            {Array.isArray(regions) && regions.length > 0 ? (
              regions.map((r) => (
                <option
                  key={r?.region_id || Math.random().toString()}
                  value={r?.region_id || ""}
                >
                  {r?.region_name || r?.region_id || "Unknown Region"}
                </option>
              ))
            ) : (
              <option value="IN-MH">Maharashtra</option>
            )}
          </select>
          <select
            value={disease}
            onChange={(e) => setDisease(e.target.value)}
            aria-label="Select disease"
            className="bg-white border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-300"
          >
            {Array.isArray(diseases) && diseases.length > 0 ? (
              diseases.map((d) => (
                <option
                  key={d?.disease_id || Math.random().toString()}
                  value={d?.disease_id || ""}
                >
                  {d?.name || d?.disease_id || "Unknown Disease"}
                </option>
              ))
            ) : (
              <option value="DENGUE">Dengue Fever</option>
            )}
          </select>
        </div>
      </div>

      {regionError && (
        <div
          role="alert"
          className="bg-white/60 backdrop-blur-md p-4 border border-terracotta-500/30 rounded-xl bg-terracotta-50 text-terracotta-600"
        >
          <p className="text-sm font-medium">{regionError}</p>
          <p className="text-xs text-red-200/80 mt-1">
            Check backend route availability and DB connectivity for regions.
          </p>
        </div>
      )}

      {/* Pipeline Execution Panel */}
      <PipelineExecutionPanel disease={disease} onComplete={loadMetrics} />

      {/* Summary Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          icon={<AlertTriangle className="w-5 h-5 text-amber-400" />}
          label="Active Alerts"
          value={alertCount ?? 0}
          subtext={`For ${disease || "current disease"}`}
          color="bg-amber-500/10"
        />
        <MetricCard
          icon={<MapPin className="w-5 h-5 text-blue-400" />}
          label="Regions Monitored"
          value={regionsCount ?? 0}
          color="bg-blue-500/10"
        />
        <MetricCard
          icon={<Activity className="w-5 h-5 text-emerald-400" />}
          label="Diseases Tracked"
          value={(diseases || []).length || "—"}
          color="bg-emerald-500/10"
        />
        <MetricCard
          icon={<BarChart2 className="w-5 h-5 text-purple-400" />}
          label="Forecast MAPE"
          value={avgMape != null ? `${(avgMape * 100).toFixed(1)}%` : "—"}
          subtext="Avg prediction error"
          color="bg-purple-500/10"
        />
      </div>

      {/* Critical Metrics Section */}
      <section>
        <h2 className="text-xs font-serif font-semibold uppercase tracking-wider text-slate-500 mb-4">
          Resource Demand
        </h2>
        <BedShortageWidget
          regionId={regionId}
          disease={disease}
          capacityThreshold={100}
        />
      </section>

      {/* Main Grid: Map and News Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <section>
            <h2 className="text-xs font-serif font-semibold uppercase tracking-wider text-slate-500 mb-4">
              Operational Map
            </h2>
            <Suspense fallback={<MapLoading />}>
              <OperationalMap disease={disease} />
            </Suspense>
          </section>
        </div>
        <div className="lg:col-span-1">
          <section className="h-full">
            <h2 className="text-xs font-serif font-semibold uppercase tracking-wider text-slate-500 mb-4">
              Intelligence Signals
            </h2>
            <EarlyWarningFeed disease={disease} />
          </section>
        </div>
      </div>
    </div>
  );
}
