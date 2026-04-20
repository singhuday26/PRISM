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
          <h1 className="text-2xl font-serif font-bold text-slate-800 mb-2">Analysis</h1>
          <p className="text-slate-500">
            Predictive modeling and historical trend analysis.
          </p>
        </div>
        <div className="flex gap-3 items-center">
          <select
            value={regionId}
            onChange={(e) => setRegionId(e.target.value)}
            className="bg-white border border-slate-200 rounded-lg px-3 py-2 text-sm font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#E07A5F]/40 shadow-sm"
          >
            <option value="" className="text-slate-500">All Regions</option>
            {regions.map((r) => (
              <option key={r.region_id} value={r.region_id}>
                {r.region_name}
              </option>
            ))}
          </select>
          <select
            value={disease}
            onChange={(e) => setDisease(e.target.value)}
            className="bg-white border border-slate-200 rounded-lg px-3 py-2 text-sm font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#E07A5F]/40 shadow-sm"
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
          <button
            onClick={loadData}
            disabled={loading}
            className="p-2 bg-[#E07A5F]/10 text-[#E07A5F] rounded-lg hover:bg-[#E07A5F]/20 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* Forecast Chart */}
      <div className="bg-white/60 backdrop-blur-md p-6 border border-slate-200 rounded-xl shadow-sm">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2.5 rounded-lg bg-blue-50 border border-blue-100">
            <Activity className="w-5 h-5 text-blue-500" />
          </div>
          <h3 className="text-lg font-serif font-bold text-slate-800">
            Forecast Model <span className="text-slate-500 font-sans font-medium text-sm ml-2">({regionId || 'All'} • {disease})</span>
          </h3>
        </div>

        <div className="h-[350px] w-full">
          {loading ? (
            <Skeleton className="w-full h-full bg-slate-100" />
          ) : forecasts?.forecasts?.length ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={forecasts.forecasts} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="date" stroke="#94a3b8" tick={{ fill: '#64748b', fontSize: 12 }} dy={10} />
                <YAxis stroke="#94a3b8" tick={{ fill: '#64748b', fontSize: 12 }} dx={-10} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#ffffff",
                    border: "1px solid #e2e8f0",
                    borderRadius: "0.5rem",
                    boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                  }}
                  itemStyle={{ color: "#334155" }}
                  labelStyle={{ color: "#64748b", marginBottom: "4px" }}
                />
                <Legend wrapperStyle={{ paddingTop: "20px" }} />
                <Line
                  type="monotone"
                  dataKey="pred_mean"
                  stroke="#E07A5F"
                  strokeWidth={3}
                  activeDot={{ r: 6, fill: "#E07A5F", stroke: "#ffffff", strokeWidth: 2 }}
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
            <div className="flex flex-col items-center justify-center h-full gap-3 text-slate-500 bg-slate-50 rounded-lg border border-dashed border-slate-200 p-6">
              <span className="text-2xl opacity-80">📊</span>
              <p className="text-sm font-medium">No forecast data for this selection</p>
              {regionId && (
                <p className="text-xs text-slate-500 text-center max-w-xs">
                  ARIMA forecasts may not have been generated for <strong className="text-slate-700">{regionId}</strong>.
                  Try selecting <strong className="text-slate-700">All Regions</strong> or run the pipeline from the Dashboard.
                </p>
              )}
            </div>
          )}
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
              {evaluation.top_regions && evaluation.top_regions.length > 0 && (() => {
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
                  {evaluation.top_regions?.slice(0, 5).map((region, i) => (
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
                  {(!evaluation.top_regions || evaluation.top_regions.length === 0) && (
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
            ) : forecasts?.forecasts && forecasts.forecasts.length > 0 ? (
              <div className="space-y-4">
                <p className="text-slate-700 text-sm leading-relaxed">
                  Based on the current predictive model (ARIMA), {disease} cases in <strong className="text-slate-900">{regionId || 'Overall'}</strong> are expected to
                  <strong className={
                    forecasts.forecasts[forecasts.forecasts.length - 1].pred_mean > forecasts.forecasts[0].pred_mean
                      ? " text-[#E07A5F]"
                      : " text-emerald-600"
                  }>
                    {forecasts.forecasts[forecasts.forecasts.length - 1].pred_mean > forecasts.forecasts[0].pred_mean
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
