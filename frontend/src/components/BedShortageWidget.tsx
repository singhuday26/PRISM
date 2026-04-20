import { useEffect, useState } from "react";
import {
  Bed,
  HeartPulse,
  Users,
  Wind,
  AlertTriangle,
  Activity,
} from "lucide-react";
import {
  predictResources,
  getTodayISO,
  type ResourcePrediction,
} from "../lib/api";

interface MetricCardProps {
  label: string;
  demand: number;
  capacity?: number;
  occupied?: number;
  icon: React.ReactNode;
  status: "critical" | "warning" | "safe";
}

function getWidthClass(utilization: number): string {
  if (utilization >= 95) return "w-full";
  if (utilization >= 90) return "w-11/12";
  if (utilization >= 80) return "w-5/6";
  if (utilization >= 75) return "w-3/4";
  if (utilization >= 65) return "w-2/3";
  if (utilization >= 50) return "w-1/2";
  if (utilization >= 35) return "w-1/3";
  if (utilization >= 20) return "w-1/4";
  if (utilization >= 10) return "w-1/6";
  return "w-[8%]";
}

function MetricCard({
  label,
  demand,
  capacity = 0,
  occupied = 0,
  icon,
  status,
}: MetricCardProps) {
  const statusClasses = {
    critical: "border-red-300 bg-red-100/70",
    warning: "border-orange-300 bg-orange-100/70",
    safe: "border-green-300 bg-green-100/70",
  };

  const accentClasses = {
    critical: "text-red-600",
    warning: "text-orange-600",
    safe: "text-green-600",
  };

  const progressClasses = {
    critical: "bg-red-500",
    warning: "bg-orange-500",
    safe: "bg-green-500",
  };

  const pillClasses = {
    critical: "bg-red-100 text-red-700 border-red-200",
    warning: "bg-orange-100 text-orange-700 border-orange-200",
    safe: "bg-green-100 text-green-700 border-green-200",
  };

  const safeDemand = Math.max(0, Number(demand ?? 0));
  const safeCapacity = Math.max(0, Number(capacity ?? 0));
  const safeOccupied = Math.max(0, Number(occupied ?? 0));

  // Capacity stress is projected load against total capacity.
  const projectedLoad = safeOccupied + safeDemand;
  const utilization =
    safeCapacity > 0 ? Math.min(100, (projectedLoad / safeCapacity) * 100) : 0;

  return (
    <div
      className={`border rounded-xl p-5 transition-all duration-300 hover:shadow-md ${statusClasses[status]}`}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div
            className={`p-2 rounded-lg bg-white shadow-sm border border-slate-100 ${accentClasses[status]}`}
          >
            {icon}
          </div>
          <span className="text-sm font-medium text-slate-600 uppercase tracking-wider">
            {label}
          </span>
        </div>
        {status === "critical" && (
          <AlertTriangle className="w-4 h-4 text-red-500 animate-pulse" />
        )}
      </div>

      <div className="space-y-4">
        <div className="flex items-end justify-between">
          <div>
            <div
              className={`text-2xl font-serif font-bold ${accentClasses[status]}`}
            >
              {safeDemand}
              <span className="text-sm font-sans font-normal text-slate-400 ml-1">
                needed
              </span>
            </div>
          </div>
          <div className="text-right">
            <div
              className={`inline-flex items-center px-2 py-0.5 rounded-full border text-[10px] font-bold ${pillClasses[status]}`}
            >
              {utilization.toFixed(0)}% LOAD
            </div>
          </div>
        </div>

        {/* Utilization Bar */}
        <div className="space-y-1.5">
          <div className="h-1.5 w-full bg-slate-200/50 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-1000 ${progressClasses[status]} ${getWidthClass(utilization)}`}
            />
          </div>
          <div className="flex justify-between text-[10px] font-medium text-slate-400 uppercase">
            <span>Used: {safeOccupied}</span>
            <span>Total: {safeCapacity}</span>
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
  regionId = "IN-MH",
  disease = "DENGUE",
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

        const normalized =
          (prediction as ResourcePrediction & { data?: ResourcePrediction })
            .data ?? prediction;
        if (!normalized || !normalized.resources) {
          console.warn("Missing resource payload", prediction);
          throw new Error("Missing resource payload");
        }

        setData(normalized);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to fetch prediction",
        );
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
        <span className="text-sm font-medium">
          Failed to sync resources for {regionId}: {error}
        </span>
      </div>
    );
  }

  if (!data) return null;

  const { resources, forecasted_cases, shortage_risk } = data;

  if (!resources) {
    console.warn("Missing resource payload", data);
    return null;
  }

  // Status logic is now dynamic from backend shortage_risk
  // We also provide local per-metric status
  const getStatus = (needed: number, occupied: number, total: number) => {
    const demand = Math.max(0, Number(needed ?? 0));
    const current = Math.max(0, Number(occupied ?? 0));
    const capacity = Math.max(0, Number(total ?? 0));
    const util = capacity > 0 ? (demand + current) / capacity : 0;
    if (util > 0.9) return "critical";
    if (util > 0.75) return "warning";
    return "safe";
  };

  const generalBedsDemand = resources.general_beds ?? 0;
  const generalBedsCapacity = resources.general_beds_capacity ?? 0;
  const generalBedsOccupied = resources.general_beds_occupied ?? 0;

  const icuDemand = resources.icu_beds ?? 0;
  const icuCapacity = resources.icu_beds_capacity ?? 0;
  const icuOccupied = resources.icu_beds_occupied ?? 0;

  const ventilatorDemand = resources.ventilators ?? 0;
  const ventilatorCapacity = resources.ventilators_capacity ?? 0;
  const ventilatorOccupied = resources.ventilators_occupied ?? 0;

  const nursesDemand = resources.nurses ?? 0;
  const nursesOnDuty = resources.nurses_on_duty ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-4">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-terracotta-500" />
          <span className="text-sm font-medium text-slate-500">
            Analyzing{" "}
            <span className="text-slate-800 font-bold">
              {forecasted_cases ?? 0}
            </span>{" "}
            predicted cases in {regionId}
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
          demand={generalBedsDemand}
          capacity={generalBedsCapacity}
          occupied={generalBedsOccupied}
          icon={<Bed className="w-5 h-5" />}
          status={getStatus(
            generalBedsDemand,
            generalBedsOccupied,
            generalBedsCapacity,
          )}
        />
        <MetricCard
          label="ICU capacity"
          demand={icuDemand}
          capacity={icuCapacity}
          occupied={icuOccupied}
          icon={<HeartPulse className="w-5 h-5" />}
          status={getStatus(icuDemand, icuOccupied, icuCapacity)}
        />
        <MetricCard
          label="Ventilators"
          demand={ventilatorDemand}
          capacity={ventilatorCapacity}
          occupied={ventilatorOccupied}
          icon={<Wind className="w-5 h-5" />}
          status={getStatus(
            ventilatorDemand,
            ventilatorOccupied,
            ventilatorCapacity,
          )}
        />
        <MetricCard
          label="Nurses"
          demand={nursesDemand}
          capacity={nursesOnDuty}
          occupied={0}
          icon={<Users className="w-5 h-5" />}
          status={getStatus(nursesDemand, 0, nursesOnDuty)}
        />
      </div>
    </div>
  );
}
