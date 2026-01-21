/**
 * PRISM Risk Heatmap - Interactive Map Logic
 * Uses Leaflet.js for map rendering with risk data overlay
 */

// Configuration
const API_BASE = window.location.origin;
const DEFAULT_CENTER = [20.5937, 78.9629]; // India center
const DEFAULT_ZOOM = 5;

// Risk level colors
const RISK_COLORS = {
    CRITICAL: '#ef4444',
    HIGH: '#f97316',
    MEDIUM: '#eab308',
    LOW: '#22c55e',
    DEFAULT: '#9ca3af'
};

// State
let map;
let markersLayer;
let currentData = [];

/**
 * Initialize the map and load data
 */
function initMap() {
    // Create map
    map = L.map('map').setView(DEFAULT_CENTER, DEFAULT_ZOOM);
    
    // Add tile layer (OpenStreetMap)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 18
    }).addTo(map);
    
    // Create markers layer group
    markersLayer = L.layerGroup().addTo(map);
    
    // Set default date to today
    const dateInput = document.getElementById('date-slider');
    dateInput.value = new Date().toISOString().split('T')[0];
    
    // Load initial data
    loadRiskData();
    
    // Setup event listeners
    setupEventListeners();
    
    updateStatus('Map initialized');
}

/**
 * Setup UI event listeners
 */
function setupEventListeners() {
    // Refresh button
    document.getElementById('refresh-btn').addEventListener('click', loadRiskData);
    
    // Disease filter change
    document.getElementById('disease-filter').addEventListener('change', loadRiskData);
    
    // Date change
    document.getElementById('date-slider').addEventListener('change', loadRiskData);
}

/**
 * Load risk data from API
 */
async function loadRiskData() {
    showLoading(true);
    updateStatus('Loading risk data...');
    
    try {
        const disease = document.getElementById('disease-filter').value;
        const date = document.getElementById('date-slider').value;
        
        // Build URL with query params
        let url = `${API_BASE}/risk/geojson`;
        const params = new URLSearchParams();
        if (disease) params.append('disease', disease);
        if (date) params.append('date', date);
        if (params.toString()) url += '?' + params.toString();
        
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const geojson = await response.json();
        currentData = geojson.features || [];
        
        // Clear existing markers
        markersLayer.clearLayers();
        
        // Add new markers
        currentData.forEach(feature => {
            const marker = createRiskMarker(feature);
            if (marker) markersLayer.addLayer(marker);
        });
        
        // Update status
        const meta = geojson.metadata || {};
        updateStatus(`Loaded ${currentData.length} regions`);
        document.getElementById('region-count').textContent = 
            `${currentData.length} regions | Date: ${meta.date || 'Latest'}`;
        
    } catch (error) {
        console.error('Error loading risk data:', error);
        updateStatus(`Error: ${error.message}`, true);
    } finally {
        showLoading(false);
    }
}

/**
 * Create a risk marker for a GeoJSON feature
 */
function createRiskMarker(feature) {
    const props = feature.properties || {};
    const geometry = feature.geometry;
    
    if (!geometry || !geometry.coordinates) return null;
    
    const coords = geometry.coordinates;
    const latLng = [coords[1], coords[0]]; // GeoJSON is [lng, lat]
    
    // Get marker color based on risk level
    const color = RISK_COLORS[props.risk_level?.toUpperCase()] || RISK_COLORS.DEFAULT;
    
    // Create circle marker with risk-based styling
    const marker = L.circleMarker(latLng, {
        radius: getMarkerRadius(props.risk_score),
        fillColor: color,
        color: '#ffffff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.8
    });
    
    // Add popup with risk details
    marker.bindPopup(createPopupContent(props));
    
    // Add hover effect
    marker.on('mouseover', function() {
        this.setStyle({
            radius: getMarkerRadius(props.risk_score) + 3,
            weight: 3
        });
    });
    
    marker.on('mouseout', function() {
        this.setStyle({
            radius: getMarkerRadius(props.risk_score),
            weight: 2
        });
    });
    
    return marker;
}

/**
 * Calculate marker radius based on risk score
 */
function getMarkerRadius(score) {
    // Scale from 8 (low) to 20 (high)
    return 8 + (score || 0) * 12;
}

/**
 * Create popup HTML content
 */
function createPopupContent(props) {
    const riskLevel = props.risk_level || 'UNKNOWN';
    const riskLevelClass = riskLevel.toLowerCase();
    
    const drivers = props.drivers || [];
    const driversHtml = drivers.length > 0 
        ? `<div class="popup-drivers">
             <h5>Risk Drivers</h5>
             <ul>${drivers.map(d => `<li>${formatDriver(d)}</li>`).join('')}</ul>
           </div>`
        : '';
    
    return `
        <div class="popup-content">
            <div class="popup-header">${props.region_name || props.region_id}</div>
            <div class="popup-row">
                <span class="popup-label">Risk Score</span>
                <span class="popup-value">${(props.risk_score || 0).toFixed(3)}</span>
            </div>
            <div class="popup-row">
                <span class="popup-label">Risk Level</span>
                <span class="risk-badge ${riskLevelClass}">${riskLevel}</span>
            </div>
            <div class="popup-row">
                <span class="popup-label">Disease</span>
                <span class="popup-value">${props.disease || 'ALL'}</span>
            </div>
            <div class="popup-row">
                <span class="popup-label">Date</span>
                <span class="popup-value">${formatDate(props.date)}</span>
            </div>
            ${driversHtml}
        </div>
    `;
}

/**
 * Format a driver string for display
 */
function formatDriver(driver) {
    return driver
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
}

/**
 * Format date for display
 */
function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    try {
        return new Date(dateStr).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch {
        return dateStr;
    }
}

/**
 * Show/hide loading indicator
 */
function showLoading(show) {
    const loading = document.getElementById('loading');
    if (show) {
        loading.classList.remove('hidden');
    } else {
        loading.classList.add('hidden');
    }
}

/**
 * Update status bar
 */
function updateStatus(message, isError = false) {
    const statusText = document.getElementById('status-text');
    statusText.textContent = message;
    statusText.style.color = isError ? '#ef4444' : '#22c55e';
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initMap);
