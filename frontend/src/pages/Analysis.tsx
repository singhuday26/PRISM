import { useState, useEffect, useCallback } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Activity, BarChart2, RefreshCw } from "lucide-react";
import {
  fetchLatestForecasts,
  fetchEvaluationSummary,
  fetchRegions,
  fetchDiseases,
  type ForecastsResponse,
  type EvaluationSummary,
  type Region,
  type DiseaseInfo,
} from "../lib/api";
import { Skeleton } from "../components/ui/Skeleton";
import { useToast } from "../context/ToastContext";

export function Analysis() {
  const [forecasts, setForecasts] = useState<ForecastsResponse | null>(null);
  const [evaluation, setEvaluation] = useState<EvaluationSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [regionId, setRegionId] = useState("IN-MH");
  const [disease, setDisease] = useState("DENGUE");
  const [regions, setRegions] = useState<Region[]>([]);
  const [diseases, setDiseases] = useState<DiseaseInfo[]>([]);
  const { error } = useToast();

  useEffect(() => {
    fetchRegions()
      .then((r) => setRegions(r.regions))
      .catch((e) => {
        console.error(e);
        error("Failed to load regions");
      });
    fetchDiseases()
      .then((d) => setDiseases(d.diseases))
      .catch((e) => {
        console.error(e);
        error("Failed to load diseases");
      });
  }, [error]);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [forecastData, evalData] = await Promise.all([
        fetchLatestForecasts(regionId, disease),
        fetchEvaluationSummary(disease),
      ]);
      setForecasts(forecastData);
      setEvaluation(evalData);
    } catch (err) {
      console.error("Failed to load analysis data", err);
      error("Failed to load analysis data");
    } finally {
      setLoading(false);
    }
  }, [regionId, disease, error]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white mb-2">Analysis</h1>
          <p className="text-gray-400">
            Predictive modeling and historical trend analysis.
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
            onClick={loadData}
            disabled={loading}
            className="p-2 bg-blue-600/20 text-blue-400 rounded-lg hover:bg-blue-600/30 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* Forecast Chart */}
      <div className="glass-card p-6 border border-white/5 rounded-xl">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2.5 rounded-lg bg-blue-500/10">
            <Activity className="w-5 h-5 text-blue-400" />
          </div>
          <h3 className="text-lg font-semibold text-white">
            Forecast Model <span className="text-gray-400 text-sm ml-2">({regionId} • {disease})</span>
          </h3>
        </div>

        <div className="h-[350px] w-full">
          {loading ? (
            <Skeleton className="w-full h-full" />
          ) : forecasts?.forecasts?.length ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={forecasts.forecasts} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                <XAxis dataKey="date" stroke="#666" tick={{ fill: '#666', fontSize: 12 }} dy={10} />
                <YAxis stroke="#666" tick={{ fill: '#666', fontSize: 12 }} dx={-10} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: "0.5rem",
                    boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.5)",
                  }}
                  itemStyle={{ color: "#e2e8f0" }}
                  labelStyle={{ color: "#94a3b8", marginBottom: "4px" }}
                />
                <Legend wrapperStyle={{ paddingTop: "20px" }} />
                <Line
                  type="monotone"
                  dataKey="pred_mean"
                  stroke="#818cf8"
                  strokeWidth={3}
                  activeDot={{ r: 6, fill: "#818cf8", stroke: "#0f172a", strokeWidth: 2 }}
                  name="Predicted Cases"
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="cases"
                  stroke="#34d399"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  name="Actual Cases"
                  dot={{ r: 3, fill: "#34d399", strokeWidth: 0 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-500 bg-white/5 rounded-lg border border-dashed border-white/10">
              No forecast data available for this selection
            </div>
          )}
        </div>
      </div>

      {/* Model Evaluation Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-card p-6 border border-white/5 rounded-xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2.5 rounded-lg bg-purple-500/10">
              <BarChart2 className="w-5 h-5 text-purple-400" />
            </div>
            <h3 className="text-lg font-semibold text-white">
              Model Performance
            </h3>
          </div>

          {loading ? (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <Skeleton className="h-24 w-full" />
                <Skeleton className="h-24 w-full" />
              </div>
              <Skeleton className="h-40 w-full" />
            </div>
          ) : evaluation ? (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-white/5 border border-white/10 text-center flex flex-col items-center justify-center">
                  <div className="text-3xl font-bold text-white mb-1">
                    {evaluation.aggregate_mae != null ? evaluation.aggregate_mae.toFixed(1) : "—"}
                  </div>
                  <div className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">
                    Mean Abs Error
                  </div>
                </div>
                <div className="p-4 rounded-xl bg-white/5 border border-white/10 text-center flex flex-col items-center justify-center">
                  <div className="text-3xl font-bold text-white mb-1">
                    {evaluation.aggregate_mape != null ? `${(evaluation.aggregate_mape * 100).toFixed(1)}%` : "—"}
                  </div>
                  <div className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">
                    MAPE
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-3 flex items-center justify-between">
                  <span>Top Performing Regions</span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-gray-300">By Error %</span>
                </h4>
                <div className="space-y-2">
                  {evaluation.top_regions?.slice(0, 5).map((region, i) => (
                    <div
                      key={region.region_id}
                      className="flex justify-between items-center px-3 py-2 rounded-lg hover:bg-white/5 transition-colors border border-transparent hover:border-white/5"
                    >
                      <span className="text-sm text-gray-300 font-medium flex items-center gap-3">
                        <span className="text-gray-600 text-xs w-4">{i + 1}.</span> {region.region_id}
                      </span>
                      <span className="text-sm font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">
                        {(region.mape * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                  {(!evaluation.top_regions || evaluation.top_regions.length === 0) && (
                    <div className="text-sm text-gray-500 text-center py-4 border border-dashed border-white/10 rounded-lg">
                      No region evaluation data
                    </div>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-gray-500 text-center py-8">
              No evaluation data available
            </div>
          )}
        </div>

        {/* Insights */}
        <div className="glass-card p-6 border border-white/5 rounded-xl flex flex-col">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" /> AI Insights
          </h3>

          <div className="flex-1 rounded-xl bg-gradient-to-br from-indigo-500/5 to-purple-500/5 border border-indigo-500/10 p-5">
            {loading ? (
              <div className="space-y-3">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-5/6" />
                <Skeleton className="h-4 w-4/6" />
              </div>
            ) : forecasts?.forecasts && forecasts.forecasts.length > 0 ? (
              <div className="space-y-4">
                <p className="text-slate-300 text-sm leading-relaxed">
                  Based on the current predictive model (ARIMA), {disease} cases in <strong className="text-white">{regionId}</strong> are expected to
                  <strong className={
                    forecasts.forecasts[forecasts.forecasts.length - 1].pred_mean > forecasts.forecasts[0].pred_mean
                      ? " text-amber-400"
                      : " text-emerald-400"
                  }>
                    {forecasts.forecasts[forecasts.forecasts.length - 1].pred_mean > forecasts.forecasts[0].pred_mean
                      ? " increase "
                      : " decrease "}
                  </strong>
                  over the next forecast horizon.
                </p>
                <div className="pt-4 border-t border-white/5">
                  <h4 className="text-xs font-semibold text-indigo-400 uppercase tracking-wider mb-2">Recommendation</h4>
                  <p className="text-sm text-slate-400 leading-relaxed">
                    Verify stock of critical medical supplies and hospital bed availability in anticipation of this trend. Set up automated alerts if projected cases exceed historical thresholds.
                  </p>
                </div>
              </div>
            ) : (
              <div className="text-gray-500 text-sm italic">
                Insufficient data to generate insights for this region and disease combination.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
