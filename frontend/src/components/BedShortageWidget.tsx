import { useEffect, useState } from 'react';
import { Bed, HeartPulse, Users, Wind, AlertTriangle, TrendingUp } from 'lucide-react';
import { predictResources, getTodayISO, type ResourcePrediction } from '../lib/api';

interface MetricCardProps {
    label: string;
    value: number;
    icon: React.ReactNode;
    status: 'critical' | 'warning' | 'safe';
    subtitle?: string;
}

function MetricCard({ label, value, icon, status, subtitle }: MetricCardProps) {
    const statusClasses = {
        critical: 'status-critical text-red-400',
        warning: 'status-warning text-amber-400',
        safe: 'status-safe text-emerald-400',
    };

    return (
        <div className={`glass-card p-6 ${statusClasses[status]}`}>
            <div className="flex items-start justify-between mb-4">
                <div className="p-2 rounded-lg bg-white/5">
                    {icon}
                </div>
                {status === 'critical' && (
                    <AlertTriangle className="w-5 h-5 text-red-400 animate-pulse" />
                )}
            </div>
            <div className="metric-value mb-1">{value}</div>
            <div className="metric-label">{label}</div>
            {subtitle && (
                <div className="mt-2 text-xs text-gray-400 flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" />
                    {subtitle}
                </div>
            )}
        </div>
    );
}

interface BedShortageWidgetProps {
    regionId?: string;
    disease?: string;
    capacityThreshold?: number;
}

export function BedShortageWidget({
    regionId = 'IN-MH',
    disease = 'dengue',
    capacityThreshold = 100
}: BedShortageWidgetProps) {
    const [data, setData] = useState<ResourcePrediction | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function fetchData() {
            try {
                setLoading(true);
                setError(null);
                const prediction = await predictResources({
                    region_id: regionId,
                    date: getTodayISO(),
                    disease: disease,
                });
                setData(prediction);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to fetch data');
            } finally {
                setLoading(false);
            }
        }

        fetchData();
        // Refresh every 30 seconds for real-time feel
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, [regionId, disease]);

    if (loading) {
        return (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {[...Array(4)].map((_, i) => (
                    <div key={i} className="glass-card p-6 animate-pulse">
                        <div className="h-8 bg-white/10 rounded mb-4 w-12" />
                        <div className="h-12 bg-white/10 rounded mb-2 w-20" />
                        <div className="h-4 bg-white/10 rounded w-16" />
                    </div>
                ))}
            </div>
        );
    }

    if (error) {
        return (
            <div className="glass-card p-6 status-critical">
                <div className="flex items-center gap-3">
                    <AlertTriangle className="w-6 h-6 text-red-400" />
                    <div>
                        <div className="font-semibold text-red-400">Connection Error</div>
                        <div className="text-sm text-gray-400">{error}</div>
                    </div>
                </div>
            </div>
        );
    }

    if (!data) return null;

    const { resources, forecasted_cases } = data;

    // Determine status based on capacity threshold
    const bedStatus = resources.general_beds > capacityThreshold ? 'critical' :
        resources.general_beds > capacityThreshold * 0.7 ? 'warning' : 'safe';
    const icuStatus = resources.icu_beds > 20 ? 'critical' :
        resources.icu_beds > 10 ? 'warning' : 'safe';
    const nurseStatus = resources.nurses > 50 ? 'critical' :
        resources.nurses > 30 ? 'warning' : 'safe';
    const oxygenStatus = resources.oxygen_cylinders > 20 ? 'critical' :
        resources.oxygen_cylinders > 10 ? 'warning' : 'safe';

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-white">
                    Resource Demand — {disease.toUpperCase()}
                </h2>
                <span className="text-sm text-gray-400">
                    Region: {regionId} • {forecasted_cases} forecasted cases
                </span>
            </div>

            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard
                    label="Beds Needed"
                    value={resources.general_beds}
                    icon={<Bed className="w-5 h-5" />}
                    status={bedStatus}
                    subtitle={bedStatus === 'critical' ? 'Over capacity!' : undefined}
                />
                <MetricCard
                    label="ICU Beds"
                    value={resources.icu_beds}
                    icon={<HeartPulse className="w-5 h-5" />}
                    status={icuStatus}
                />
                <MetricCard
                    label="Nurses"
                    value={resources.nurses}
                    icon={<Users className="w-5 h-5" />}
                    status={nurseStatus}
                />
                <MetricCard
                    label="O₂ Cylinders"
                    value={resources.oxygen_cylinders}
                    icon={<Wind className="w-5 h-5" />}
                    status={oxygenStatus}
                />
            </div>
        </div>
    );
}
