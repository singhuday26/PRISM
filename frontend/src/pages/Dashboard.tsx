import { Suspense, lazy } from "react";
import { BedShortageWidget } from "../components/BedShortageWidget";

// Lazy load the map component to prevent SSR/hydration issues
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

export function Dashboard() {
    return (
        <div className="space-y-8">
            {/* Page Title */}
            <div>
                <h1 className="text-2xl font-bold text-white mb-2">mission control</h1>
                <p className="text-gray-400">
                    Real-time resource allocation and outbreak monitoring
                </p>
            </div>

            {/* Critical Metrics Section */}
            <section>
                <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-4">
                    Critical Metrics
                </h2>
                <BedShortageWidget
                    regionId="IN-MH"
                    disease="DENGUE"
                    capacityThreshold={100}
                />
            </section>

            {/* Operational Map Section */}
            <section>
                <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-4">
                    Operational Map
                </h2>
                <Suspense fallback={<MapLoading />}>
                    <OperationalMap disease="DENGUE" />
                </Suspense>
            </section>
        </div>
    );
}
