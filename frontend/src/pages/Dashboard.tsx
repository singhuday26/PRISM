import { Suspense, lazy, useState, useEffect } from "react";
import { BedShortageWidget } from "../components/BedShortageWidget";
import {
  fetchRegions,
  fetchDiseases,
  type Region,
  type DiseaseInfo,
} from "../lib/api";

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
  const [regionId, setRegionId] = useState("IN-MH");
  const [disease, setDisease] = useState("DENGUE");
  const [regions, setRegions] = useState<Region[]>([]);
  const [diseases, setDiseases] = useState<DiseaseInfo[]>([]);

  useEffect(() => {
    fetchRegions()
      .then((r) => setRegions(r.regions))
      .catch((e) => console.error("Failed to load regions", e));
    fetchDiseases()
      .then((d) => setDiseases(d.diseases))
      .catch((e) => console.error("Failed to load diseases", e));
  }, []);

  return (
    <div className="space-y-8">
      {/* Page Title + Selectors */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white mb-2">
            mission control
          </h1>
          <p className="text-gray-400">
            Real-time resource allocation and outbreak monitoring
          </p>
        </div>
        <div className="flex gap-3">
          <select
            value={regionId}
            onChange={(e) => setRegionId(e.target.value)}
            className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40"
          >
            {regions.map((r) => (
              <option
                key={r.region_id}
                value={r.region_id}
                className="bg-gray-900"
              >
                {r.region_name}
              </option>
            ))}
            {regions.length === 0 && (
              <option value="IN-MH" className="bg-gray-900">
                Maharashtra
              </option>
            )}
          </select>
          <select
            value={disease}
            onChange={(e) => setDisease(e.target.value)}
            className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40"
          >
            {diseases.map((d) => (
              <option
                key={d.disease_id}
                value={d.disease_id}
                className="bg-gray-900"
              >
                {d.name}
              </option>
            ))}
            {diseases.length === 0 && (
              <option value="DENGUE" className="bg-gray-900">
                Dengue Fever
              </option>
            )}
          </select>
        </div>
      </div>

      {/* Critical Metrics Section */}
      <section>
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-4">
          Critical Metrics
        </h2>
        <BedShortageWidget
          regionId={regionId}
          disease={disease}
          capacityThreshold={100}
        />
      </section>

      {/* Operational Map Section */}
      <section>
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-4">
          Operational Map
        </h2>
        <Suspense fallback={<MapLoading />}>
          <OperationalMap disease={disease} />
        </Suspense>
      </section>
    </div>
  );
}
