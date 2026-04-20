import { useEffect, useState } from "react";
import { AlertTriangle } from "lucide-react";
import { MapContainer, TileLayer, GeoJSON, ScaleControl } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { fetchRiskGeoJSON, type GeoJSONResponse } from "../lib/api";

// Indian center coordinates
const CENTER: [number, number] = [20.5937, 78.9629];
const ZOOM = 5;

// Color scale based on risk level
function getRiskColor(riskScore: number): string {
  if (riskScore >= 0.7) return "#ef4444"; // Red (Critical)
  if (riskScore >= 0.5) return "#f97316"; // Orange (High)
  if (riskScore >= 0.3) return "#eab308"; // Yellow (Medium)
  return "#22c55e"; // Green (Low)
}

function getRiskLevel(riskScore: number): string {
  if (riskScore >= 0.7) return "CRITICAL";
  if (riskScore >= 0.5) return "HIGH";
  if (riskScore >= 0.3) return "MEDIUM";
  return "LOW";
}

interface OperationalMapProps {
  disease?: string;
}

export function OperationalMap({ disease }: OperationalMapProps) {
  const [geoData, setGeoData] = useState<GeoJSONResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch GeoJSON data
  useEffect(() => {
    async function initMap() {
      try {
        setLoading(true);
        const data = await fetchRiskGeoJSON(disease);
        setGeoData(data);
        setError(null);
      } catch (err) {
        console.error("Map data fetch error:", err);
        setError("Failed to load map data. Backend may be offline.");
      } finally {
        setLoading(false);
      }
    }

    initMap();
  }, [disease]);

  const onEachFeature = (feature: GeoJSON.Feature, layer: L.Layer) => {
    const {
      region_name,
      risk_score,
      disease: featDisease,
      date,
    } = feature.properties || {};

    const pathLayer = layer as L.Path;

    // Only style if layer supports setStyle (polygons, not markers)
    if (typeof pathLayer.setStyle === "function") {
      pathLayer.setStyle({
        fillColor: getRiskColor(risk_score || 0),
        weight: 1,
        opacity: 1,
        color: "white",
        fillOpacity: 0.6,
      });
    }

    const safeRiskScore = risk_score || 0;
    const riskLevel = getRiskLevel(safeRiskScore);
    const color = getRiskColor(safeRiskScore);

    const popupContent = `
      <div class="p-2 min-w-[200px] text-gray-900">
        <h3 class="font-bold text-lg border-b pb-1 mb-2">${region_name || "Unknown"}</h3>
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-semibold">Risk Score:</span>
          <span class="font-bold px-2 py-0.5 rounded text-white text-sm" style="background-color: ${color}">
            ${safeRiskScore.toFixed(2)} (${riskLevel})
          </span>
        </div>
        <div class="text-xs text-gray-600 mb-1">
          <strong>Disease:</strong> ${featDisease || "N/A"}
        </div>
        <div class="text-xs text-gray-600 mb-2">
          <strong>Date:</strong> ${date || "N/A"}
        </div>
      </div>
    `;
    pathLayer.bindPopup(popupContent);

    // Highlight on hover - only for layers that support styling
    if (typeof pathLayer.setStyle === "function") {
      pathLayer.on({
        mouseover: (e: L.LeafletMouseEvent) => {
          const l = e.target as L.Path;
          if (typeof l.setStyle === "function") {
            l.setStyle({
              weight: 2,
              color: "#666",
              fillOpacity: 0.8,
            });
            l.bringToFront();
          }
        },
        mouseout: (e: L.LeafletMouseEvent) => {
          const l = e.target as L.Path;
          if (typeof l.setStyle === "function") {
            l.setStyle({
              weight: 1,
              color: "white",
              fillOpacity: 0.6,
            });
          }
        },
      });
    }
  };

  // Convert Point geometries to CircleMarkers with risk-based styling
  const pointToLayer = (
    feature: GeoJSON.Feature,
    latlng: L.LatLng,
  ): L.Layer => {
    const riskScore = feature.properties?.risk_score || 0;
    return L.circleMarker(latlng, {
      radius: 8,
      fillColor: getRiskColor(riskScore),
      color: "white",
      weight: 1,
      opacity: 1,
      fillOpacity: 0.7,
    });
  };

  // Style function for polygon/line geometries
  const style = (feature: GeoJSON.Feature | undefined) => {
    const riskScore = feature?.properties?.risk_score || 0;
    return {
      fillColor: getRiskColor(riskScore),
      weight: 1,
      opacity: 1,
      color: "white",
      fillOpacity: 0.6,
    };
  };

  if (loading) {
    return (
      <div className="h-[500px] bg-white/60 backdrop-blur-md flex items-center justify-center border border-slate-200 rounded-xl shadow-none">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-slate-400 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-slate-500 text-sm">Fetching map data...</p>
        </div>
      </div>
    );
  }

  if (error || !geoData || !geoData.features || geoData.features.length === 0) {
    return (
      <div className="h-[500px] bg-white/60 backdrop-blur-md flex flex-col items-center justify-center text-slate-500 p-8 text-center border border-slate-200 rounded-xl shadow-none">
        <AlertTriangle className="w-12 h-12 mb-4 text-terracotta-500 opacity-50" />
        <h3 className="text-lg font-serif text-slate-800 mb-2">
          Map Data Unavailable
        </h3>
        <p className="max-w-md text-sm text-slate-500 mb-4">
          {error || "No geographic risk data found for this selection."}
        </p>
        <div className="text-xs bg-slate-100 p-4 rounded text-left font-mono">
          <p className="mb-1 text-slate-500">// Debug Info:</p>
          <p className="text-slate-700">
            GET /api/risk/geojson -&gt; {error ? "Failed" : "Empty Features"}
          </p>
          <p className="text-slate-700">Disease: {disease || "All"}</p>
        </div>
      </div>
    );
  }

  // Render map only when Leaflet is ready
  return (
    <div className="h-[600px] w-full bg-white/60 backdrop-blur-md overflow-hidden rounded-xl border border-slate-200 shadow-none relative z-0">
      <MapContainer
        center={CENTER}
        zoom={ZOOM}
        style={{ height: "100%", width: "100%", background: "#FAFAFA" }}
        scrollWheelZoom={false}
      >
        {/* Light Matter Tiles for "Pristine Lab" look */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        />

        <GeoJSON
          data={geoData}
          style={style}
          pointToLayer={pointToLayer}
          onEachFeature={onEachFeature}
        />

        <ScaleControl position="bottomleft" />
      </MapContainer>

      {/* Risk Legend Overlay */}
      <div className="absolute bottom-6 right-6 bg-white/80 backdrop-blur-md border border-slate-200 p-4 rounded-xl shadow-none z-[1000] pointer-events-none">
        <h4 className="text-xs font-semibold font-serif text-slate-800 uppercase tracking-wider mb-2">
          Risk Levels
        </h4>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-[#ef4444]"></span>
            <span className="text-xs text-slate-600">Critical (&gt;0.7)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-[#f97316]"></span>
            <span className="text-xs text-slate-600">High (&gt;0.5)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-[#eab308]"></span>
            <span className="text-xs text-slate-600">Medium (&gt;0.3)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-[#22c55e]"></span>
            <span className="text-xs text-slate-600">Low (&lt;0.3)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
