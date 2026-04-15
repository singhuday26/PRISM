/**
 * PRISM Command API Client
 * Connects to the backend Resource Intelligence API
 */

function resolveApiBase(): string {
  const configured = import.meta.env.VITE_API_BASE as string | undefined;
  if (configured && configured.trim().length > 0) {
    const base = configured.trim();
    if (base.startsWith("http")) return base;
    return base.startsWith("/") ? base : `/${base}`;
  }

  // If VITE_API_BASE is not set, we are running locally (or deployed but unconfigured).
  // Because the FastAPI backend now correctly mounts all API routes under /api,
  // we can safely use /api for both vite dev proxy and local python deployments!
  return "/api";
}

const API_BASE = resolveApiBase();

export function buildApiPath(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${normalized}`;
}

// --- Auth Helpers ---

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem("prism_token");
  if (token) {
    return { Authorization: `Bearer ${token}` };
  }
  return {};
}

async function authFetch(url: string, init?: RequestInit): Promise<Response> {
  const headers = {
    ...getAuthHeaders(),
    ...(init?.headers || {}),
  };
  const response = await fetch(url, { ...init, headers });
  if (response.status === 401) {
    const token = localStorage.getItem("prism_token");
    // Only redirect if user had a real token (not demo mode)
    if (token) {
      localStorage.removeItem("prism_token");
      const loginPath = window.location.pathname.startsWith("/ui")
        ? "/ui/login"
        : "/login";
      if (
        !window.location.pathname.includes("/login") &&
        window.location.pathname !== "/"
      ) {
        window.location.href = loginPath;
      }
    }
    throw new Error("Authentication required for this action in demo mode.");
  }
  return response;
}

// --- Resources ---

export interface ResourceDemand {
  general_beds: number;
  icu_beds: number;
  nurses: number;
  oxygen_cylinders: number;
}

export interface ResourcePrediction {
  region_id: string;
  date: string;
  disease: string;
  forecasted_cases: number;
  resources: ResourceDemand;
  shortage_risk: boolean;
}

export interface PredictResourcesParams {
  region_id: string;
  date: string;
  disease: string;
}

// --- GeoJSON ---

export interface GeoJSONFeature {
  type: "Feature";
  properties: {
    region_id: string;
    region_name: string;
    risk_score: number;
    risk_level: string;
    disease: string;
    date: string;
    [key: string]: string | number | boolean | null | undefined;
  };
  geometry: {
    type: "Polygon" | "MultiPolygon";
    coordinates: number[] | number[][] | number[][][] | number[][][][];
  };
}

export interface GeoJSONResponse {
  type: "FeatureCollection";
  features: GeoJSONFeature[];
  metadata?: Record<string, unknown>;
}

// --- Forecasts ---

export interface ForecastItem {
  date: string;
  pred_mean: number;
  pred_lower: number;
  pred_upper: number;
  region_id: string;
  model_version: string;
  source_granularity?: string;
  disease?: string;
  generated_at?: string;
  cases?: number;
}

export interface ForecastsResponse {
  date: string | null;
  forecasts: ForecastItem[];
  count: number;
  granularity?: string;
  disease?: string;
}

// --- Evaluation ---

export interface EvaluationResult {
  region_id: string;
  horizon: number;
  mae: number;
  mape: number;
  mse: number;
  rmse: number;
  r2: number;
  points_compared?: number;
  error?: string;
}

export interface EvaluationSummary {
  regions_evaluated: number;
  horizon: number;
  aggregate_mae: number | null;
  aggregate_mape: number | null;
  disease?: string;
  top_regions: EvaluationResult[];
}

// --- Reports ---

export interface GenerateReportResponse {
  report_id: string;
  status: string;
  estimated_time_seconds: number;
}

export interface ReportStatusResponse {
  report_id: string;
  type: string;
  status: string;
  download_url?: string;
  generated_at?: string;
  error?: string;
}

export interface ReportItem {
  report_id: string;
  type: string;
  status: string;
  generated_at: string;
  region_id?: string;
  disease?: string;
}

export interface ReportListResponse {
  reports: ReportItem[];
  count: number;
}

// --- Notifications ---

export interface SubscribeRequest {
  email: string;
  regions?: string[];
  diseases?: string[];
  frequency?: "immediate" | "daily"; // default immediate
  min_risk_level?: "MEDIUM" | "HIGH" | "CRITICAL"; // default HIGH
}

export interface SubscribeResponse {
  message: string;
  subscriber_id: string;
  email: string;
}

// --- Regions & Diseases ---

export interface Region {
  region_id: string;
  region_name: string;
  population: number;
  lat: number;
  lon: number;
}

export interface RegionsResponse {
  regions: Region[];
  count: number;
}

export interface DiseaseInfo {
  disease_id: string;
  name: string;
  description: string;
  transmission_mode: string;
  severity: string;
}

export interface DiseasesResponse {
  count: number;
  diseases: DiseaseInfo[];
}

// --- Alerts (typed) ---

export interface Alert {
  region_id: string;
  date: string;
  risk_level: string;
  /** @deprecated use risk_level instead — kept for backward compat */
  severity?: string;
  disease?: string;
  reason?: string;
  risk_score?: number;
}

export interface AlertsResponse {
  date: string | null;
  alerts: Alert[];
  count: number;
  disease?: string;
}

// --- News ---

export interface NewsArticle {
  id?: string;
  title: string;
  source: string;
  url?: string;
  published_at: string;
  content: string;
  extracted_diseases: string[];
  extracted_locations: string[];
  relevance_score: number;
}

export interface NewsResponse {
  articles: NewsArticle[];
  count: number;
  disease?: string;
}

// --- Pipeline ---

export interface PipelineStepResult {
  name: string;
  status: "success" | "error" | "skipped";
  duration_ms: number;
  records_created: number;
  total_records: number;
  detail: string;
}

export interface PipelineTaskStatus {
  task_id: string;
  disease: string;
  status: "queued" | "processing" | "completed" | "failed";
  created_at: string;
  started_at?: string;
  completed_at?: string;
  params: {
    reset: boolean;
    horizon: number;
    granularity: string;
  };
  steps: PipelineStepResult[];
  progress: number;
  error?: string;
  duration_seconds?: number;
}

export interface PipelineTaskResponse {
  task_id: string;
  message: string;
  status_url: string;
}

export interface PipelineRunResponse {
  success: boolean;
  disease: string;
  reset: boolean;
  horizon: number;
  granularity: string;
  execution_date: string | null;
  duration_seconds: number;
  steps: PipelineStepResult[];
  created: {
    risk_scores: number;
    alerts: number;
    forecasts: number;
  };
  total: {
    risk_scores: number;
    alerts: number;
    forecasts: number;
  };
}

// --- Auth ---

export interface User {
  id?: string;
  username: string;
  email: string;
  role: string;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  role?: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface LoginError {
  detail: string;
}

// --- API Functions ---

/**
 * Fetch all regions
 */
export async function fetchRegions(): Promise<RegionsResponse> {
  const response = await fetch(`${API_BASE}/regions/`);
  if (!response.ok) {
    throw new Error(`Failed to fetch regions: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch all diseases
 */
export async function fetchDiseases(): Promise<DiseasesResponse> {
  const response = await fetch(`${API_BASE}/diseases/`);
  if (!response.ok) {
    throw new Error(`Failed to fetch diseases: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch resource predictions from the backend
 */
export async function predictResources(
  params: PredictResourcesParams,
): Promise<ResourcePrediction> {
  const searchParams = new URLSearchParams({
    date: params.date,
    disease: params.disease,
  });

  const response = await authFetch(
    `${API_BASE}/resources/predict?region_id=${params.region_id}&${searchParams}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    },
  );

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch Risk GeoJSON data
 */
export async function fetchRiskGeoJSON(
  disease?: string,
): Promise<GeoJSONResponse> {
  const params = new URLSearchParams();
  if (disease) params.append("disease", disease);

  const response = await fetch(`${API_BASE}/risk/geojson?${params}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch GeoJSON: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get today's date in ISO format
 */
export function getTodayISO(): string {
  return new Date().toISOString().split("T")[0];
}

/**
 * Fetch latest forecasts
 */
export async function fetchLatestForecasts(
  region_id?: string,
  disease?: string,
  horizon: number = 7,
): Promise<ForecastsResponse> {
  const params = new URLSearchParams();
  if (region_id) params.append("region_id", region_id);
  if (disease) params.append("disease", disease);
  params.append("horizon", horizon.toString());

  const response = await fetch(`${API_BASE}/forecasts/latest?${params}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch forecasts: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Generate forecasts (calls backend to generate, might be slow)
 */
export async function generateForecasts(
  date?: string,
  horizon: number = 7,
  disease?: string,
  granularity: string = "monthly",
): Promise<ForecastsResponse> {
  const params = new URLSearchParams();
  if (date) params.append("date", date);
  params.append("horizon", horizon.toString());
  if (disease) params.append("disease", disease);
  params.append("granularity", granularity);

  const response = await authFetch(`${API_BASE}/forecasts/generate?${params}`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error(`Failed to generate forecasts: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get evaluation summary
 */
export async function fetchEvaluationSummary(
  disease?: string,
  horizon: number = 7,
  granularity: string = "monthly",
): Promise<EvaluationSummary> {
  const params = new URLSearchParams();
  if (disease) params.append("disease", disease);
  params.append("horizon", horizon.toString());
  params.append("granularity", granularity);

  const response = await fetch(`${API_BASE}/evaluation/summary?${params}`);
  if (!response.ok) {
    throw new Error(
      `Failed to fetch evaluation summary: ${response.statusText}`,
    );
  }
  return response.json();
}

/**
 * List reports
 */
export async function listReports(
  region_id?: string,
  disease?: string,
  limit: number = 20,
): Promise<ReportListResponse> {
  const params = new URLSearchParams();
  if (region_id) params.append("region_id", region_id);
  if (disease) params.append("disease", disease);
  params.append("limit", limit.toString());

  const response = await fetch(`${API_BASE}/reports/list?${params}`);
  if (!response.ok) {
    throw new Error(`Failed to list reports: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Generate a report
 */
export async function generateReport(
  type: "weekly_summary" | "region_detail" | "disease_overview",
  region_id?: string,
  disease?: string,
  period_start?: string,
  period_end?: string,
): Promise<GenerateReportResponse> {
  const response = await authFetch(`${API_BASE}/reports/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      type,
      region_id,
      disease,
      period_start,
      period_end,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || `Failed to generate report`);
  }
  return response.json();
}

/**
 * Subscribe to notifications
 */
export async function subscribe(
  data: SubscribeRequest,
): Promise<SubscribeResponse> {
  const response = await authFetch(`${API_BASE}/notifications/subscribe`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to subscribe: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch latest alerts
 */
export async function fetchAlerts(
  region_id?: string,
  disease?: string,
  limit: number = 20,
): Promise<AlertsResponse> {
  const params = new URLSearchParams();
  if (region_id) params.append("region_id", region_id);
  if (disease) params.append("disease", disease);
  params.append("limit", limit.toString());

  const response = await fetch(`${API_BASE}/alerts/latest?${params}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch alerts: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch latest news articles
 */
export async function fetchNews(
  disease?: string,
  limit: number = 10,
): Promise<NewsResponse> {
  const params = new URLSearchParams();
  if (disease) params.append("disease", disease);
  params.append("limit", limit.toString());

  const response = await fetch(`${API_BASE}/intelligence/?${params}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch news: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Trigger simulated news ingestion
 */
export async function ingestSimulatedNews(): Promise<{ message: string }> {
  const response = await authFetch(`${API_BASE}/news/ingest-simulated`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error(`Failed to ingest news: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Run the analytics pipeline for a disease (starts background task)
 */
export async function runPipeline(
  disease: string,
  options?: { reset?: boolean; horizon?: number; granularity?: string },
): Promise<PipelineTaskResponse> {
  const params = new URLSearchParams();
  params.append("disease", disease);
  if (options?.reset) params.append("reset", "true");
  if (options?.horizon) params.append("horizon", options.horizon.toString());
  if (options?.granularity) params.append("granularity", options.granularity);

  const response = await authFetch(`${API_BASE}/pipeline/run?${params}`, {
    method: "POST",
  });
  if (!response.ok) {
    const err = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(err.detail || "Pipeline execution failed");
  }
  return response.json();
}

/**
 * Fetch the status of a background pipeline task
 */
export async function fetchTaskStatus(
  taskId: string,
): Promise<PipelineTaskStatus> {
  const response = await fetch(`${API_BASE}/pipeline/status/${taskId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch task status: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Login and get token
 */
export async function login(
  username: string,
  password: string,
): Promise<Token> {
  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);

  const response = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(async () => {
      const text = await response.text().catch(() => "");
      return { detail: text || response.statusText || "Login failed" };
    });
    throw new Error(error.detail || "Login failed");
  }

  const token: Token = await response.json();
  localStorage.setItem("prism_token", token.access_token);
  return token;
}

/**
 * Register a new user
 */
export async function register(data: UserCreate): Promise<User> {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(async () => {
      const text = await response.text().catch(() => "");
      return { detail: text || response.statusText || "Registration failed" };
    });
    throw new Error(error.detail || "Registration failed");
  }

  return response.json();
}

/**
 * Get current user
 */
export async function fetchMe(): Promise<User> {
  const token = localStorage.getItem("prism_token");
  if (!token) throw new Error("No token found");

  const response = await fetch(`${API_BASE}/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch user profile");
  }

  return response.json();
}

/**
 * Update current user's profile (username, email)
 */
export async function updateProfile(data: {
  username?: string;
  email?: string;
}): Promise<User> {
  const response = await authFetch(`${API_BASE}/auth/me`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const err = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(err.detail || "Failed to update profile");
  }
  return response.json();
}

/**
 * Change the current user's password
 */
export async function changePassword(data: {
  current_password: string;
  new_password: string;
}): Promise<{ message: string }> {
  const response = await authFetch(`${API_BASE}/auth/change-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const err = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(err.detail || "Failed to change password");
  }
  return response.json();
}

// --- Ecosystem Wing ---

export type InstitutionType =
  | "hospital"
  | "ambulance"
  | "fire_station"
  | "lab"
  | "pharmacy"
  | "district_admin"
  | "police"
  | "blood_bank"
  | "wash"
  | "ngo";

export type OperationalStatus =
  | "operational"
  | "degraded"
  | "critical"
  | "offline";

export interface EcoInstitution {
  institution_id: string;
  name: string;
  type: InstitutionType;
  region_id: string;
  lat?: number;
  lon?: number;
  address?: string;
  contact_phone?: string;
  status: OperationalStatus;
  health_score: number;
  status_detail?: Record<string, unknown>;
  last_updated?: string;
}

export interface InstitutionAlert {
  alert_id: string;
  institution_id: string;
  institution_name: string;
  institution_type: string;
  region_id: string;
  severity: string;
  message: string;
  timestamp: string;
}

export interface CategorySummary {
  type: InstitutionType;
  label: string;
  count: number;
  operational: number;
  degraded: number;
  critical: number;
  offline: number;
  avg_health_score: number;
}

export interface EcoSummaryResponse {
  summary: {
    total_institutions: number;
    overall_health_score: number;
    active_alerts: number;
    categories: CategorySummary[];
  };
  alerts: InstitutionAlert[];
}

export interface EcoInstitutionsResponse {
  institutions: EcoInstitution[];
  count: number;
}

/**
 * Fetch ecosystem institutions
 */
export async function fetchInstitutions(
  type?: string,
  region_id?: string,
  search?: string,
  limit: number = 200,
): Promise<EcoInstitutionsResponse> {
  const params = new URLSearchParams();
  if (type) params.append("type", type);
  if (region_id) params.append("region_id", region_id);
  if (search) params.append("search", search);
  params.append("limit", limit.toString());

  const response = await fetch(`${API_BASE}/ecosystem/institutions?${params}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch institutions: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch single institution detail
 */
export async function fetchInstitutionDetail(
  id: string,
): Promise<EcoInstitution> {
  const response = await fetch(`${API_BASE}/ecosystem/institutions/${id}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch institution: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch ecosystem summary with alerts
 */
export async function fetchEcosystemSummary(): Promise<EcoSummaryResponse> {
  const response = await fetch(`${API_BASE}/ecosystem/summary`);
  if (!response.ok) {
    throw new Error(
      `Failed to fetch ecosystem summary: ${response.statusText}`,
    );
  }
  return response.json();
}
