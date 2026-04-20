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
  const [regionId, setRegionId] = useState(""); // empty = all regions
  const [disease, setDisease] = useState("DENGUE");
  const [regions, setRegions] = useState<Region[]>([]);
  const [diseases, setDiseases] = useState<DiseaseInfo[]>([]);
  const { error } = useToast();

  useEffect(() => {
    fetchRegions()
      .then((r) => setRegions(r && Array.isArray(r.regions) ? r.regions : []))
      .catch((e) => {
        console.error(e);
        error("Failed to load regions");
      });
    fetchDiseases()
      .then((d) => setDiseases(d && Array.isArray(d.diseases) ? d.diseases : []))
      .catch((e) => {
        console.error(e);
        error("Failed to load diseases");
      });
  }, [error]);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [forecastData, evalData] = await Promise.all([
        fetchLatestForecasts(regionId || undefined, disease),
        fetchEvaluationSummary(disease, 7, "monthly"),
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
          <h1 className="text-2xl font-serif font-bold text-slate-800 mb-2">
            Regional Analysis
          </h1>
          <p className="text-slate-500">
            Historical trends and AI-driven forecasting models.
          </p>
        </div>
        <div className="flex gap-3 items-center">
          <select
            value={regionId}
            onChange={(e) => setRegionId(e.target.value)}
            className="bg-white border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-300"
          >
            <option value="">All Regions</option>
            {(Array.isArray(regions) ? regions : []).map((r) => (
              <option key={r?.region_id || Math.random()} value={r?.region_id || ""}>
                {r?.region_name || r?.region_id || "Unknown Region"}
              </option>
            ))}
          </select>
          <select
            value={disease}
            onChange={(e) => setDisease(e.target.value)}
            className="bg-white border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-300"
          >
            {(Array.isArray(diseases) ? diseases : []).map((d) => (
              <option key={d?.disease_id || Math.random()} value={d?.disease_id || ""}>
                {d?.name || d?.disease_id || "Unknown Disease"}
              </option>
            ))}
          </select>
          <button
            onClick={loadData}
            disabled={loading}
            className="p-2 bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-600 transition-colors disabled:opacity-50"
            title="Refresh Data"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Forecast Chart */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white/60 backdrop-blur-md border border-slate-200 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-6">
              <Activity className="w-5 h-5 text-terracotta-500" />
              <h2 className="text-lg font-serif font-bold text-slate-800">
                Case Forecast (ARIMA-7)
              </h2>
            </div>

            <div className="h-[400px] w-full">
              {loading ? (
                <div className="h-full w-full flex items-center justify-center bg-slate-50/50 rounded-lg">
                  <Skeleton className="h-full w-full opacity-20" />
                </div>
              ) : forecasts?.forecasts && Array.isArray(forecasts.forecasts) && forecasts.forecasts.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={forecasts.forecasts}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis
                      dataKey="date"
                      tick={{ fontSize: 10, fill: "#94a3b8" }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fontSize: 10, fill: "#94a3b8" }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "rgba(255, 255, 255, 0.9)",
                        borderRadius: "8px",
                        border: "1px solid #e2e8f0",
                        boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                      }}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="pred_mean"
                      name="Predicted Cases"
                      stroke="#E07A5F"
                      strokeWidth={3}
                      dot={{ r: 4, fill: "#E07A5F", strokeWidth: 0 }}
                      activeDot={{ r: 6 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="pred_upper"
                      name="Upper Bound (95%)"
                      stroke="#cbd5e1"
                      strokeDasharray="5 5"
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="pred_lower"
                      name="Lower Bound (95%)"
                      stroke="#cbd5e1"
                      strokeDasharray="5 5"
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full w-full flex flex-col items-center justify-center bg-slate-50/50 rounded-lg text-slate-400 border border-dashed border-slate-200">
                   <p className="text-sm">No forecast data available for this selection.</p>
                   <p className="text-xs mt-1">Try running the pipeline in Mission Control.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Model Evaluation Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white/60 backdrop-blur-md p-6 border border-slate-200 rounded-xl shadow-sm">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2.5 rounded-lg bg-purple-50 border border-purple-100">
              <BarChart2 className="w-5 h-5 text-purple-500" />
            </div>
            <h3 className="text-lg font-serif font-bold text-slate-800">
              Model Performance
            </h3>
          </div>

          {loading ? (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <Skeleton className="h-24 w-full bg-slate-100" />
                <Skeleton className="h-24 w-full bg-slate-100" />
              </div>
              <Skeleton className="h-40 w-full bg-slate-100" />
            </div>
          ) : evaluation ? (
            <div className="space-y-6">
              {/* Top-level aggregate metrics */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-blue-50 border border-blue-100 text-center flex flex-col items-center justify-center">
                  <div className="text-3xl font-serif font-bold text-blue-700 mb-1">
                    {evaluation.aggregate_mae != null ? evaluation.aggregate_mae.toFixed(1) : "—"}
                  </div>
                  <div className="text-[10px] text-blue-500 uppercase tracking-wider font-semibold">Mean Abs Error</div>
                </div>
                <div className="p-4 rounded-xl bg-purple-50 border border-purple-100 text-center flex flex-col items-center justify-center">
                  <div className="text-3xl font-serif font-bold text-purple-700 mb-1">
                    {evaluation.aggregate_mape != null ? `${(evaluation.aggregate_mape * 100).toFixed(1)}%` : "—"}
                  </div>
                  <div className="text-[10px] text-purple-500 uppercase tracking-wider font-semibold">MAPE</div>
                </div>
              </div>

              {/* Secondary metrics from top region */}
              {Array.isArray(evaluation.top_regions) && evaluation.top_regions.length > 0 && (() => {
                const best = evaluation.top_regions[0];
                return (
                  <div className="grid grid-cols-3 gap-3">
                    <div className="p-3 rounded-xl bg-white border border-slate-200 shadow-sm text-center">
                      <div className="text-lg font-bold text-emerald-600">
                        {best.rmse != null ? best.rmse.toFixed(1) : "—"}
                      </div>
                      <div className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold mt-0.5">RMSE</div>
                    </div>
                    <div className="p-3 rounded-xl bg-white border border-slate-200 shadow-sm text-center">
                      <div className="text-lg font-bold text-amber-600">
                        {best.mse != null ? best.mse.toFixed(1) : "—"}
                      </div>
                      <div className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold mt-0.5">MSE</div>
                    </div>
                    <div className="p-3 rounded-xl bg-white border border-slate-200 shadow-sm text-center">
                      <div className="text-lg font-bold text-indigo-600">
                        {best.r2 != null ? best.r2.toFixed(3) : "—"}
                      </div>
                      <div className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold mt-0.5">R²</div>
                    </div>
                  </div>
                );
              })()}

              {/* Per-region leaderboard */}
              <div>
                <h4 className="text-sm font-medium text-slate-600 mb-3 flex items-center justify-between">
                  <span>Top Performing Regions</span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200">By MAE</span>
                </h4>
                <div className="space-y-2">
                  {(Array.isArray(evaluation.top_regions) ? evaluation.top_regions : [])?.slice(0, 5).map((region, i) => (
                    <div
                      key={region.region_id}
                      className="flex justify-between items-center px-3 py-2 rounded-lg bg-white border border-slate-200 hover:border-slate-300 transition-colors shadow-sm"
                    >
                      <span className="text-sm text-slate-800 font-medium flex items-center gap-3">
                        <span className="text-slate-400 text-xs w-4">{i + 1}.</span>
                        {region.region_id}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono text-slate-500">
                          MAE {region.mae?.toFixed(1) ?? "—"}
                        </span>
                        <span className="text-sm font-mono text-emerald-600 bg-emerald-50 border border-emerald-100 px-2 py-0.5 rounded">
                          {region.mape != null ? `${(region.mape * 100).toFixed(1)}%` : "—"}
                        </span>
                      </div>
                    </div>
                  ))}
                  {(!Array.isArray(evaluation.top_regions) || evaluation.top_regions.length === 0) && (
                    <div className="text-sm text-slate-500 text-center py-4 border border-dashed border-slate-200 rounded-lg">
                      No region evaluation data available
                    </div>
                  )}
                </div>
              </div>

              {/* Regions evaluated count */}
              <p className="text-xs text-slate-500 text-right">
                {evaluation.regions_evaluated} region{evaluation.regions_evaluated !== 1 ? "s" : ""} evaluated
              </p>
            </div>
          ) : (
            <div className="text-slate-500 text-center py-8">
              No evaluation data available
            </div>
          )}
        </div>

        {/* Insights */}
        <div className="bg-white/60 backdrop-blur-md p-6 border border-slate-200 rounded-xl shadow-sm flex flex-col">
          <h3 className="text-lg font-serif font-bold text-slate-800 mb-4 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#E07A5F] animate-pulse" /> AI Insights
          </h3>

          <div className="flex-1 rounded-xl bg-slate-50 border border-slate-200 p-5 shadow-sm">
            {loading ? (
              <div className="space-y-3">
                <Skeleton className="h-4 w-full bg-slate-200" />
                <Skeleton className="h-4 w-5/6 bg-slate-200" />
                <Skeleton className="h-4 w-4/6 bg-slate-200" />
              </div>
            ) : forecasts?.forecasts && Array.isArray(forecasts.forecasts) && forecasts.forecasts.length > 0 ? (
              <div className="space-y-4">
                <p className="text-slate-700 text-sm leading-relaxed">
                  Based on the current predictive model (ARIMA), {disease} cases in <strong className="text-slate-900">{regionId || 'Overall'}</strong> are expected to
                  <strong className={
                    forecasts.forecasts.length > 0 && 
                    forecasts.forecasts[forecasts.forecasts.length - 1].pred_mean > forecasts.forecasts[0].pred_mean
                      ? " text-[#E07A5F]"
                      : " text-emerald-600"
                  }>
                    {forecasts.forecasts.length > 0 && 
                     forecasts.forecasts[forecasts.forecasts.length - 1].pred_mean > forecasts.forecasts[0].pred_mean
                      ? " increase "
                      : " decrease "}
                  </strong>
                  over the next forecast horizon.
                </p>
                <div className="pt-4 border-t border-slate-200">
                  <h4 className="text-xs font-semibold text-slate-800 uppercase tracking-wider mb-2 font-serif">Recommendation</h4>
                  <p className="text-sm text-slate-600 leading-relaxed">
                    Verify stock of critical medical supplies and hospital bed availability in anticipation of this trend. Set up automated alerts if projected cases exceed historical thresholds.
                  </p>
                </div>
              </div>
            ) : (
              <div className="text-slate-500 text-sm italic">
                Insufficient data to generate insights for this region and disease combination.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
