import { useEffect, useState } from 'react';
import { Bed, HeartPulse, Users, Wind, AlertTriangle, TrendingUp, Activity } from 'lucide-react';
import { predictResources, getTodayISO, type ResourcePrediction } from '../lib/api';

interface MetricCardProps {
    label: string;
    demand: number;
    capacity?: number;
    occupied?: number;
    icon: React.ReactNode;
    status: 'critical' | 'warning' | 'safe';
    unit?: string;
}

function MetricCard({ label, demand, capacity = 0, occupied = 0, icon, status, unit = "" }: MetricCardProps) {
    const statusClasses = {
        critical: 'border-red-200 bg-red-50/30',
        warning: 'border-amber-200 bg-amber-50/30',
        safe: 'border-emerald-200 bg-emerald-50/30',
    };

    const accentClasses = {
        critical: 'text-red-600',
        warning: 'text-amber-600',
        safe: 'text-emerald-600',
    };

    const progressClasses = {
        critical: 'bg-red-500',
        warning: 'bg-amber-500',
        safe: 'bg-emerald-500',
    };

    // Total projected load: current + new predicted
    const projectedLoad = occupied + demand;
    const utilization = capacity > 0 ? Math.min(100, (projectedLoad / capacity) * 100) : 0;

    return (
        <div className={`border rounded-xl p-5 transition-all duration-300 hover:shadow-md ${statusClasses[status]}`}>
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg bg-white shadow-sm border border-slate-100 ${accentClasses[status]}`}>
                        {icon}
                    </div>
                    <span className="text-sm font-medium text-slate-600 uppercase tracking-wider">{label}</span>
                </div>
                {status === 'critical' && (
                    <AlertTriangle className="w-4 h-4 text-red-500 animate-pulse" />
                )}
            </div>

            <div className="space-y-4">
                <div className="flex items-end justify-between">
                    <div>
                        <div className="text-2xl font-serif font-bold text-slate-800">
                            {demand}<span className="text-sm font-sans font-normal text-slate-400 ml-1">needed</span>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className={`text-xs font-bold ${accentClasses[status]}`}>
                            {utilization.toFixed(0)}% LOAD
                        </div>
                    </div>
                </div>

                {/* Utilization Bar */}
                <div className="space-y-1.5">
                    <div className="h-1.5 w-full bg-slate-200/50 rounded-full overflow-hidden">
                        <div 
                            className={`h-full transition-all duration-1000 ${progressClasses[status]}`}
                            style={{ width: `${utilization}%` }}
                        />
                    </div>
                    <div className="flex justify-between text-[10px] font-medium text-slate-400 uppercase">
                        <span>Used: {occupied}</span>
                        <span>Total: {capacity}</span>
                    </div>
                </div>
            </div>
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
    disease = 'DENGUE',
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
                setError(err instanceof Error ? err.message : 'Failed to fetch prediction');
            } finally {
                setLoading(false);
            }
        }

        fetchData();
        const interval = setInterval(fetchData, 60000); // 1-minute refresh
        return () => clearInterval(interval);
    }, [regionId, disease]);

    if (loading) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[...Array(4)].map((_, i) => (
                    <div key={i} className="h-32 bg-slate-50 animate-pulse rounded-xl" />
                ))}
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6 bg-red-50 border border-red-100 rounded-xl text-red-600 flex items-center gap-3">
                <AlertTriangle className="w-5 h-5" />
                <span className="text-sm font-medium">Failed to sync resources for {regionId}: {error}</span>
            </div>
        );
    }

    if (!data) return null;

    const { resources, forecasted_cases, shortage_risk } = data;

    // Status logic is now dynamic from backend shortage_risk
    // We also provide local per-metric status
    const getStatus = (needed: number, occupied: number, total: number) => {
        const util = total > 0 ? (needed + occupied) / total : 0;
        if (util > 0.9) return 'critical';
        if (util > 0.7) return 'warning';
        return 'safe';
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-4">
                <div className="flex items-center gap-2">
                    <Activity className="w-4 h-4 text-terracotta-500" />
                    <span className="text-sm font-medium text-slate-500">
                        Analyzing <span className="text-slate-800 font-bold">{forecasted_cases}</span> predicted cases in {regionId}
                    </span>
                </div>
                {shortage_risk && (
                    <div className="flex items-center gap-1.5 px-3 py-1 bg-red-100 text-red-700 text-[10px] font-bold rounded-full animate-pulse border border-red-200 uppercase">
                        <AlertTriangle className="w-3 h-3" />
                        Infrastructure At Risk
                    </div>
                )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <MetricCard
                    label="Ward Beds"
                    demand={resources.general_beds}
                    capacity={resources.general_beds_capacity}
                    occupied={resources.general_beds_occupied}
                    icon={<Bed className="w-5 h-5" />}
                    status={getStatus(resources.general_beds, resources.general_beds_occupied || 0, resources.general_beds_capacity || 0)}
                />
                <MetricCard
                    label="ICU capacity"
                    demand={resources.icu_beds}
                    capacity={resources.icu_beds_capacity}
                    occupied={resources.icu_beds_occupied}
                    icon={<HeartPulse className="w-5 h-5" />}
                    status={getStatus(resources.icu_beds, resources.icu_beds_occupied || 0, resources.icu_beds_capacity || 1)}
                />
                <MetricCard
                    label="Personnel"
                    demand={resources.nurses}
                    capacity={resources.nurses_on_duty ? resources.nurses_on_duty * 2 : 100} // Mock total staff force
                    occupied={resources.nurses_on_duty}
                    icon={<Users className="w-5 h-5" />}
                    status={getStatus(resources.nurses, resources.nurses_on_duty || 0, (resources.nurses_on_duty || 50) * 2)}
                />
                <MetricCard
                    label="O₂ Inventory"
                    demand={resources.oxygen_cylinders}
                    capacity={resources.oxygen_cylinders_stock}
                    occupied={resources.oxygen_cylinders_stock ? resources.oxygen_cylinders_stock / 2 : 50} // Mock usage
                    icon={<Wind className="w-5 h-5" />}
                    status={getStatus(resources.oxygen_cylinders, (resources.oxygen_cylinders_stock || 100) / 2, resources.oxygen_cylinders_stock || 1)}
                />
            </div>
        </div>
    );
}
