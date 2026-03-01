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
import { AlertTriangle, MapPin, Activity, BarChart2, Play, RefreshCw } from "lucide-react";

const OperationalMap = lazy(() =>
  import("../components/OperationalMap").then((m) => ({
    default: m.OperationalMap,
  })),
);

function MapLoading() {
  return (
    <div className="h-[500px] glass-card flex items-center justify-center bg-[hsl(240,10%,6%)] border border-white/10 rounded-lg">
      <div className="text-center">
        <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
        <p className="text-gray-400 text-sm">Loading map component...</p>
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
    <div className="glass-card p-5 border border-white/5 rounded-xl hover:border-white/10 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div className={`p-2.5 rounded-lg ${color}`}>
          {icon}
        </div>
      </div>
      <div className="text-2xl font-bold text-white mb-1">{value}</div>
      <div className="text-xs text-gray-400 uppercase tracking-wider font-medium">{label}</div>
      {subtext && <div className="text-xs text-gray-500 mt-1">{subtext}</div>}
    </div>
  );
}

export function Dashboard() {
  const [regionId, setRegionId] = useState("IN-MH");
  const [disease, setDisease] = useState("DENGUE");
  const [regions, setRegions] = useState<Region[]>([]);
  const [diseases, setDiseases] = useState<DiseaseInfo[]>([]);

  // Metrics state
  const [alertCount, setAlertCount] = useState(0);
  const [regionsCount, setRegionsCount] = useState(0);
  const [avgMape, setAvgMape] = useState<number | null>(null);
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [pipelineStatus, setPipelineStatus] = useState<string | null>(null);

  const loadMetrics = useCallback(async () => {
    try {
      const [alertsData, regionsData, evalData] = await Promise.allSettled([
        fetchAlerts(undefined, disease, 100),
        fetchRegions(),
        fetchEvaluationSummary(disease),
      ]);

      if (alertsData.status === "fulfilled") setAlertCount(alertsData.value.count);
      if (regionsData.status === "fulfilled") {
        setRegionsCount(regionsData.value.count);
        setRegions(regionsData.value.regions);
      }
      if (evalData.status === "fulfilled" && evalData.value.aggregate_mape != null) {
        setAvgMape(evalData.value.aggregate_mape);
      }
    } catch (e) {
      console.error("Failed to load metrics", e);
    }
  }, [disease]);

  useEffect(() => {
    loadMetrics();
    fetchDiseases()
      .then((d) => setDiseases(d.diseases))
      .catch((e) => console.error("Failed to load diseases", e));
  }, [loadMetrics]);

  // Auto-refresh every 60s
  useEffect(() => {
    const interval = setInterval(loadMetrics, 60000);
    return () => clearInterval(interval);
  }, [loadMetrics]);

  const runPipeline = async () => {
    setPipelineRunning(true);
    setPipelineStatus(null);
    try {
      const response = await fetch(`/api/pipeline/run?disease=${disease}`, {
        method: "POST",
      });
      if (response.ok) {
        setPipelineStatus("Pipeline completed successfully!");
        setTimeout(() => { loadMetrics(); setPipelineStatus(null); }, 3000);
      } else {
        setPipelineStatus("Pipeline failed. Check backend logs.");
      }
    } catch {
      setPipelineStatus("Pipeline request failed.");
    } finally {
      setPipelineRunning(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Page Title + Selectors + Pipeline */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white mb-2">
            Mission Control
          </h1>
          <p className="text-gray-400">
            Real-time resource allocation and outbreak monitoring
          </p>
        </div>
        <div className="flex gap-3 items-center">
          <select
            value={regionId}
            onChange={(e) => setRegionId(e.target.value)}
            className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40"
          >
            {regions.map((r) => (
              <option key={r.region_id} value={r.region_id} className="bg-gray-900">
                {r.region_name}
              </option>
            ))}
            {regions.length === 0 && (
              <option value="IN-MH" className="bg-gray-900">Maharashtra</option>
            )}
          </select>
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
          <button
            onClick={runPipeline}
            disabled={pipelineRunning}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm text-white font-medium transition-colors"
            title="Run analytics pipeline"
          >
            {pipelineRunning ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            <span className="hidden sm:inline">Pipeline</span>
          </button>
        </div>
      </div>

      {/* Pipeline status toast */}
      {pipelineStatus && (
        <div className={`p-3 rounded-lg text-sm font-medium ${pipelineStatus.includes("success") ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-red-500/10 text-red-400 border border-red-500/20"}`}>
          {pipelineStatus}
        </div>
      )}

      {/* Summary Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          icon={<AlertTriangle className="w-5 h-5 text-amber-400" />}
          label="Active Alerts"
          value={alertCount}
          subtext={`For ${disease}`}
          color="bg-amber-500/10"
        />
        <MetricCard
          icon={<MapPin className="w-5 h-5 text-blue-400" />}
          label="Regions Monitored"
          value={regionsCount}
          color="bg-blue-500/10"
        />
        <MetricCard
          icon={<Activity className="w-5 h-5 text-emerald-400" />}
          label="Diseases Tracked"
          value={diseases.length || "—"}
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
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-4">
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
            <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-4">
              Operational Map
            </h2>
            <Suspense fallback={<MapLoading />}>
              <OperationalMap disease={disease} />
            </Suspense>
          </section>
        </div>
        <div className="lg:col-span-1">
          <section className="h-full">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-4">
              Intelligence Signals
            </h2>
            <EarlyWarningFeed disease={disease} />
          </section>
        </div>
      </div>
    </div>
  );
}
