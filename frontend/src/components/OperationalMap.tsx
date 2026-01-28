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

  const onEachFeature = (feature: any, layer: any) => {
    const {
      region_name,
      risk_score,
      disease: featDisease,
      date,
    } = feature.properties || {};

    // Only style if layer supports setStyle (polygons, not markers)
    if (typeof layer.setStyle === "function") {
      layer.setStyle({
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
    layer.bindPopup(popupContent);

    // Highlight on hover - only for layers that support styling
    if (typeof layer.setStyle === "function") {
      layer.on({
        mouseover: (e: any) => {
          const l = e.target;
          if (typeof l.setStyle === "function") {
            l.setStyle({
              weight: 2,
              color: "#666",
              fillOpacity: 0.8,
            });
            l.bringToFront();
          }
        },
        mouseout: (e: any) => {
          const l = e.target;
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
  const pointToLayer = (feature: any, latlng: L.LatLng): L.Layer => {
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
  const style = (feature: any) => {
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
      <div className="h-[500px] glass-card flex items-center justify-center bg-[hsl(240,10%,6%)] border border-white/10 rounded-lg">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-400 text-sm">Fetching map data...</p>
        </div>
      </div>
    );
  }

  if (error || !geoData || !geoData.features || geoData.features.length === 0) {
    return (
      <div className="h-[500px] glass-card flex flex-col items-center justify-center text-gray-400 p-8 text-center bg-[hsl(240,10%,6%)] border border-white/10 rounded-lg">
        <AlertTriangle className="w-12 h-12 mb-4 text-red-400 opacity-50" />
        <h3 className="text-lg font-medium text-white mb-2">
          Map Data Unavailable
        </h3>
        <p className="max-w-md text-sm text-gray-500 mb-4">
          {error || "No geographic risk data found for this selection."}
        </p>
        <div className="text-xs bg-black/30 p-4 rounded text-left font-mono">
          <p className="mb-1 text-gray-400">// Debug Info:</p>
          <p>
            GET /api/risk/geojson -&gt; {error ? "Failed" : "Empty Features"}
          </p>
          <p>Disease: {disease || "All"}</p>
        </div>
      </div>
    );
  }

  // Render map only when Leaflet is ready
  return (
    <div className="h-[600px] w-full glass-card overflow-hidden rounded-lg border border-white/10 relative z-0">
      <MapContainer
        center={CENTER}
        zoom={ZOOM}
        style={{ height: "100%", width: "100%", background: "#0a0a0f" }}
        scrollWheelZoom={false}
      >
        {/* Dark Matter Tiles for "Mission Control" look */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
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
      <div className="absolute bottom-6 right-6 bg-[hsl(240,10%,6%)]/90 backdrop-blur border border-white/10 p-4 rounded-lg shadow-xl z-[1000] pointer-events-none">
        <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
          Risk Levels
        </h4>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-[#ef4444] shadow-[0_0_10px_#ef4444]"></span>
            <span className="text-xs text-white">Critical (&gt;0.7)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-[#f97316]"></span>
            <span className="text-xs text-white">High (&gt;0.5)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-[#eab308]"></span>
            <span className="text-xs text-white">Medium (&gt;0.3)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-[#22c55e]"></span>
            <span className="text-xs text-white">Low (&lt;0.3)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
