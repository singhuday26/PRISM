import {
    Building2,
    Ambulance,
    Flame,
    FlaskConical,
    Pill,
    Landmark,
    Shield,
    Droplets,
    Heart,
    HandHeart,
} from "lucide-react";
import type { CategorySummary, InstitutionType } from "../../lib/api";

const TYPE_ICON: Record<InstitutionType, React.ElementType> = {
    hospital: Building2,
    ambulance: Ambulance,
    fire_station: Flame,
    lab: FlaskConical,
    pharmacy: Pill,
    district_admin: Landmark,
    police: Shield,
    blood_bank: Droplets,
    wash: Heart,
    ngo: HandHeart,
};

const TYPE_COLOR: Record<InstitutionType, string> = {
    hospital: "from-blue-500/20 to-blue-600/10 border-blue-500/20 text-blue-400",
    ambulance: "from-red-500/20 to-red-600/10 border-red-500/20 text-red-400",
    fire_station: "from-orange-500/20 to-orange-600/10 border-orange-500/20 text-orange-400",
    lab: "from-emerald-500/20 to-emerald-600/10 border-emerald-500/20 text-emerald-400",
    pharmacy: "from-violet-500/20 to-violet-600/10 border-violet-500/20 text-violet-400",
    district_admin: "from-amber-500/20 to-amber-600/10 border-amber-500/20 text-amber-400",
    police: "from-slate-500/20 to-slate-600/10 border-slate-500/20 text-slate-300",
    blood_bank: "from-rose-500/20 to-rose-600/10 border-rose-500/20 text-rose-400",
    wash: "from-cyan-500/20 to-cyan-600/10 border-cyan-500/20 text-cyan-400",
    ngo: "from-pink-500/20 to-pink-600/10 border-pink-500/20 text-pink-400",
};

interface Props {
    categories: CategorySummary[];
    selectedType: string;
    onSelectType: (type: string) => void;
}

export function EcosystemSummaryStrip({
    categories,
    selectedType,
    onSelectType,
}: Props) {
    return (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 xl:grid-cols-10 gap-3">
            {categories.map((cat) => {
                const Icon = TYPE_ICON[cat.type] || Building2;
                const colors = TYPE_COLOR[cat.type] || TYPE_COLOR.hospital;
                const isActive = selectedType === cat.type;

                // Health bar width
                const healthPct = Math.max(0, Math.min(100, cat.avg_health_score));

                return (
                    <button
                        key={cat.type}
                        onClick={() =>
                            onSelectType(isActive ? "" : cat.type)
                        }
                        className={`relative p-3 rounded-xl border transition-all duration-200 text-left cursor-pointer group
              ${isActive
                                ? `bg-white ring-1 ring-slate-200 border-slate-200 scale-[1.02] shadow-sm`
                                : "bg-white border-slate-100 hover:bg-slate-50 hover:border-slate-200 shadow-none"
                            }`}
                    >
                        <div className="flex items-center gap-2 mb-2">
                            <Icon className={`w-4 h-4 ${isActive ? "text-terracotta-500" : "text-slate-400"}`} />
                            <span className={`text-[10px] font-semibold uppercase tracking-wider truncate ${isActive ? "text-slate-800" : "text-slate-500"}`}>
                                {cat.label.split(" ")[0]}
                            </span>
                        </div>
                        <div className="text-xl font-serif font-bold text-slate-800 mb-1">{cat.count}</div>
                        {/* mini health bar */}
                        <div className="h-1 rounded-full bg-slate-100 overflow-hidden">
                            <div
                                className={`h-full rounded-full transition-all duration-500 ${healthPct >= 70
                                        ? "bg-emerald-500"
                                        : healthPct >= 40
                                            ? "bg-amber-400"
                                            : "bg-terracotta-500"
                                    }`}
                                style={{ width: `${healthPct}%` }}
                            />
                        </div>
                        <div className="text-[9px] text-slate-500 mt-1">
                            {healthPct.toFixed(0)}% health
                        </div>
                    </button>
                );
            })}
        </div>
    );
}

export { TYPE_ICON, TYPE_COLOR };
