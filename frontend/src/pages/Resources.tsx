import { useState, useEffect } from 'react';
import { BedShortageWidget } from '../components/BedShortageWidget';
import { fetchAlerts } from '../lib/api';
import { AlertTriangle, Plus, Search } from 'lucide-react';

export function Resources() {
    const [criticalRegions, setCriticalRegions] = useState<string[]>([]);
    const [alertsLoading, setAlertsLoading] = useState(true);
    const [customRegion, setCustomRegion] = useState('');
    const [disease, setDisease] = useState('DENGUE');

    useEffect(() => {
        async function loadCriticalRegions() {
            setAlertsLoading(true);
            try {
                const data = await fetchAlerts(undefined, disease, 10);
                // Extract unique region IDs from high/critical risk alerts
                const highRiskRegions = data.alerts
                    .filter((alert: any) => alert.risk_level === 'CRITICAL' || alert.risk_level === 'HIGH')
                    .map((alert: any) => alert.region_id);

                // Deduplicate and fallback to default if empty
                const uniqueRegions = Array.from(new Set(highRiskRegions)) as string[];
                setCriticalRegions(uniqueRegions.length > 0 ? uniqueRegions : ['IN-MH']);
            } catch (error) {
                console.error("Failed to load alerts:", error);
                setCriticalRegions(['IN-MH']); // Fallback
            } finally {
                setAlertsLoading(false);
            }
        }
        loadCriticalRegions();
    }, [disease]);

    const addRegion = () => {
        if (customRegion && !criticalRegions.includes(customRegion)) {
            setCriticalRegions([...criticalRegions, customRegion]);
            setCustomRegion('');
        }
    };

    return (
        <div className="space-y-8">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-white mb-2">Resource Allocation</h1>
                    <p className="text-gray-400">Monitor and predict healthcare resource demands.</p>
                </div>
                <div className="flex gap-4">
                    <select
                        value={disease}
                        onChange={(e) => setDisease(e.target.value)}
                        className="bg-white/5 border border-white/10 rounded px-3 py-2 text-white"
                    >
                        <option value="DENGUE">Dengue</option>
                        <option value="MALARIA">Malaria</option>
                        <option value="CHIKUNGUNYA">Chikungunya</option>
                    </select>
                </div>
            </div>

            {/* Add Custom Region */}
            <div className="glass-card p-4 flex gap-4 items-center">
                <Search className="w-5 h-5 text-gray-400" />
                <input
                    type="text"
                    placeholder="Enter Region ID (e.g., IN-MH, IN-KA)..."
                    value={customRegion}
                    onChange={(e) => setCustomRegion(e.target.value)}
                    className="bg-transparent border-none outline-none text-white flex-1"
                    onKeyDown={(e) => e.key === 'Enter' && addRegion()}
                />
                <button
                    onClick={addRegion}
                    className="p-2 bg-blue-600/20 text-blue-400 rounded hover:bg-blue-600/30"
                >
                    <Plus className="w-5 h-5" />
                </button>
            </div>

            {/* Grid of Resource Widgets */}
            <div className="space-y-8">
                {alertsLoading ? (
                    <div className="text-center py-12 text-gray-500">
                        Identifying critical regions...
                    </div>
                ) : criticalRegions.length > 0 ? (
                    criticalRegions.map(regionId => (
                        <div key={regionId} className="relative">
                            <div className="absolute -left-4 top-0 bottom-0 w-1 bg-gradient-to-b from-blue-500/50 to-transparent rounded-full" />
                            <BedShortageWidget
                                regionId={regionId}
                                disease={disease}
                                capacityThreshold={100} // This could be dynamic based on region config
                            />
                        </div>
                    ))
                ) : (
                    <div className="glass-card p-12 text-center text-gray-500">
                        <AlertTriangle className="w-12 h-12 mx-auto mb-4 opacity-50" />
                        No critical resource shortages detected.
                    </div>
                )}
            </div>
        </div>
    );
}
