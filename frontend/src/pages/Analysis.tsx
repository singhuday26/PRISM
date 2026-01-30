import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Activity, BarChart2, RefreshCw } from 'lucide-react';
import { fetchLatestForecasts, fetchEvaluationSummary, type ForecastsResponse, type EvaluationSummary } from '../lib/api';

export function Analysis() {
    const [forecasts, setForecasts] = useState<ForecastsResponse | null>(null);
    const [evaluation, setEvaluation] = useState<EvaluationSummary | null>(null);
    const [loading, setLoading] = useState(false);
    const [regionId, setRegionId] = useState('IN-MH'); // Default to Maharashtra
    const [disease, setDisease] = useState('DENGUE');

    const loadData = async () => {
        setLoading(true);
        try {
            const [forecastData, evalData] = await Promise.all([
                fetchLatestForecasts(regionId, disease),
                fetchEvaluationSummary(disease)
            ]);
            setForecasts(forecastData);
            setEvaluation(evalData);
        } catch (error) {
            console.error("Failed to load analysis data", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, [regionId, disease]);

    return (
        <div className="space-y-8">
            <div className="flex justify-between items-start">
                <div>
                    <h1 className="text-2xl font-bold text-white mb-2">Analysis</h1>
                    <p className="text-gray-400">Predictive modeling and historical trend analysis.</p>
                </div>
                <div className="flex gap-4">
                    <input
                        type="text"
                        value={regionId}
                        onChange={(e) => setRegionId(e.target.value.toUpperCase())}
                        className="bg-white/5 border border-white/10 rounded px-3 py-2 text-white w-24 text-center"
                        placeholder="Region"
                    />
                    <select
                        value={disease}
                        onChange={(e) => setDisease(e.target.value)}
                        className="bg-white/5 border border-white/10 rounded px-3 py-2 text-white"
                    >
                        <option value="DENGUE">Dengue</option>
                        <option value="MALARIA">Malaria</option>
                        <option value="CHIKUNGUNYA">Chikungunya</option>
                    </select>
                    <button
                        onClick={loadData}
                        className="p-2 bg-blue-600/20 text-blue-400 rounded hover:bg-blue-600/30 transition-colors"
                    >
                        <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                    </button>
                </div>
            </div>

            {/* Forecast Chart */}
            <div className="glass-card p-6">
                <div className="flex items-center gap-3 mb-6">
                    <Activity className="w-5 h-5 text-blue-400" />
                    <h3 className="text-lg font-semibold text-white">Forecast Model ({regionId} - {disease})</h3>
                </div>

                <div className="h-[300px] w-full">
                    {forecasts?.forecasts?.length ? (
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={forecasts.forecasts}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                                <XAxis dataKey="date" stroke="#666" />
                                <YAxis stroke="#666" />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#111', border: '1px solid #333' }}
                                    itemStyle={{ color: '#ccc' }}
                                />
                                <Legend />
                                <Line type="monotone" dataKey="cases" stroke="#3b82f6" activeDot={{ r: 8 }} name="Predicted Cases" />
                                <Line type="monotone" dataKey="cases_actual" stroke="#10b981" strokeDasharray="5 5" name="Actual Cases" />
                            </LineChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="flex items-center justify-center h-full text-gray-500">
                            {loading ? 'Loading forecasts...' : 'No forecast data available'}
                        </div>
                    )}
                </div>
            </div>

            {/* Model Evaluation Metrics */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="glass-card p-6">
                    <div className="flex items-center gap-3 mb-6">
                        <BarChart2 className="w-5 h-5 text-purple-400" />
                        <h3 className="text-lg font-semibold text-white">Model Performance</h3>
                    </div>

                    {evaluation ? (
                        <div className="space-y-6">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-4 rounded-lg bg-white/5 border border-white/10 text-center">
                                    <div className="text-2xl font-bold text-white mb-1">
                                        {evaluation.aggregate_mae?.toFixed(1) || 'N/A'}
                                    </div>
                                    <div className="text-xs text-gray-400 uppercase tracking-wider">Mean Abs Error</div>
                                </div>
                                <div className="p-4 rounded-lg bg-white/5 border border-white/10 text-center">
                                    <div className="text-2xl font-bold text-white mb-1">
                                        {evaluation.aggregate_mape ? `${(evaluation.aggregate_mape * 100).toFixed(1)}%` : 'N/A'}
                                    </div>
                                    <div className="text-xs text-gray-400 uppercase tracking-wider">MAPE</div>
                                </div>
                            </div>

                            <div>
                                <h4 className="text-sm font-medium text-gray-400 mb-3">Top Performing Regions</h4>
                                <div className="space-y-2">
                                    {evaluation.top_regions?.map((region, i) => (
                                        <div key={region.region_id} className="flex justify-between items-center p-2 rounded hover:bg-white/5">
                                            <span className="text-sm text-gray-300">
                                                {i + 1}. {region.region_id}
                                            </span>
                                            <span className="text-sm font-mono text-emerald-400">
                                                {(region.mape * 100).toFixed(1)}% err
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="text-gray-500 text-center py-8">
                            {loading ? 'Evaluating models...' : 'No evaluation data'}
                        </div>
                    )}
                </div>

                {/* Insights / Recommendations Placeholders */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Insights</h3>
                    <p className="text-gray-400 text-sm leading-relaxed">
                        Based on current trends, {disease} cases in {regionId} are expected to
                        {forecasts?.forecasts && forecasts.forecasts.length > 1 &&
                            forecasts.forecasts[forecasts.forecasts.length - 1].cases > forecasts.forecasts[0].cases
                            ? ' increase ' : ' decrease '}
                        over the next week.
                        Resource allocation should validatethe stock of critical supplies.
                    </p>
                </div>
            </div>
        </div>
    );
}
