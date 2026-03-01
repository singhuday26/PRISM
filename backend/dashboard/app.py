import os
import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import warnings

# Suppress warnings to keep logs clean
warnings.filterwarnings("ignore")

# Import Plotly and custom components
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Import custom theme
try:
    from .theme import PRISM_THEME_CSS, CHART_COLORS, get_risk_color
    from .charts import (
        create_risk_heatmap, 
        create_forecast_chart, 
        create_model_comparison_chart,
        create_hotspot_treemap,
    )
    CUSTOM_COMPONENTS = True
except ImportError:
    CUSTOM_COMPONENTS = False
    PRISM_THEME_CSS = ""

API_URL = os.getenv("API_URL", "http://localhost:8000")


# ============================================================
# Cached data-fetching helpers
# All API calls are wrapped in @st.cache_data so that a widget
# interaction (dropdown change, button click) does NOT re-fetch
# data that hasn't changed.  TTL = 5 minutes by default.
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def _api_get_diseases() -> list:
    try:
        resp = requests.get(f"{API_URL}/regions/diseases", timeout=30)
        if resp.ok:
            return resp.json().get("diseases", [])
    except Exception:
        pass
    return []


@st.cache_data(ttl=300, show_spinner=False)
def _api_get_hotspots(disease_filter: str | None) -> tuple:
    url = f"{API_URL}/hotspots"
    if disease_filter:
        url += f"?disease={disease_filter}"
    try:
        resp = requests.get(url, timeout=30)
        if resp.ok:
            return resp.json().get("hotspots", []), None
        return None, f"HTTP {resp.status_code}"
    except requests.RequestException as e:
        return None, str(e)


@st.cache_data(ttl=300, show_spinner=False)
def _api_get_risk_latest(disease_filter: str | None) -> tuple:
    url = f"{API_URL}/risk/latest"
    if disease_filter:
        url += f"?disease={disease_filter}"
    try:
        resp = requests.get(url, timeout=30)
        if resp.ok:
            data = resp.json()
            return data.get("risk_scores", []), data.get("date"), None
        return None, None, f"HTTP {resp.status_code}"
    except requests.RequestException as e:
        return None, None, str(e)


@st.cache_data(ttl=300, show_spinner=False)
def _api_get_alerts(disease_filter: str | None, limit: int = 20) -> tuple:
    url = f"{API_URL}/alerts/latest?limit={limit}"
    if disease_filter:
        url += f"&disease={disease_filter}"
    try:
        resp = requests.get(url, timeout=30)
        if resp.ok:
            data = resp.json()
            return data.get("alerts", []), data.get("date"), None
        return None, None, f"HTTP {resp.status_code}"
    except requests.RequestException as e:
        return None, None, str(e)


@st.cache_data(ttl=300, show_spinner=False)
def _api_get_regions(disease_filter: str | None) -> list:
    url = f"{API_URL}/regions"
    if disease_filter:
        url += f"?disease={disease_filter}"
    try:
        resp = requests.get(url, timeout=30)
        if resp.ok:
            return [r.get("region_id") for r in resp.json().get("regions", []) if r.get("region_id")]
    except Exception:
        pass
    return []


@st.cache_data(ttl=300, show_spinner=False)
def _api_get_forecast(region_id: str, disease_filter: str | None, horizon: int = 7) -> tuple:
    url = f"{API_URL}/forecasts/latest?region_id={region_id}&horizon={horizon}"
    if disease_filter:
        url += f"&disease={disease_filter}"
    try:
        resp = requests.get(url, timeout=60)
        if resp.ok:
            return resp.json().get("forecasts", []), None
        return None, f"HTTP {resp.status_code}"
    except requests.RequestException as e:
        return None, str(e)


@st.cache_data(ttl=300, show_spinner=False)
def _api_get_evaluation(region_id: str, horizon: int = 7) -> tuple:
    try:
        resp = requests.get(
            f"{API_URL}/evaluation/forecast?region_id={region_id}&horizon={horizon}",
            timeout=60,
        )
        if resp.ok:
            return resp.json(), None
        return None, f"HTTP {resp.status_code}"
    except requests.RequestException as e:
        return None, str(e)


def _csv_download(df: pd.DataFrame, label: str, prefix: str, disease_label: str, key: str):
    """Render a CSV download button for a DataFrame."""
    try:
        csv_data = df.to_csv(index=False).encode("utf-8")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{disease_label}_{timestamp}.csv"
        st.download_button(label=label, data=csv_data, file_name=filename, mime="text/csv", key=key)
    except Exception as e:
        st.warning(f"Unable to prepare download: {str(e)}")


def _format_alert_rows(alerts):
    """Convert raw alert dicts to display-ready rows."""
    rows = []
    for a in alerts:
        created_at = a.get("created_at", "")
        if isinstance(created_at, str):
            try:
                dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                created_at = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pass
        rows.append({
            "Region": a.get("region_id"),
            "Risk Level": a.get("risk_level"),
            "Risk Score": round(a.get("risk_score", 0), 3),
            "Reason": a.get("reason"),
            "Created At": created_at,
        })
    return rows

# Page configuration with modern settings
st.set_page_config(
    page_title="PRISM Dashboard", 
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply custom theme
if PRISM_THEME_CSS:
    st.markdown(PRISM_THEME_CSS, unsafe_allow_html=True)

st.title("🔬 PRISM: Predictive Risk Intelligence & Surveillance Model")

# Initialize session state
if 'pipeline_status' not in st.session_state:
    st.session_state.pipeline_status = None
if 'selected_disease' not in st.session_state:
    st.session_state.selected_disease = None
if 'selected_granularity' not in st.session_state:
    st.session_state.selected_granularity = "monthly"
if 'api_healthy' not in st.session_state:
    st.session_state.api_healthy = False

# Check API health on startup
def check_api_health():
    """Check if API is reachable and healthy."""
    import time
    for attempt in range(3):
        try:
            resp = requests.get(f"{API_URL}/health/ping", timeout=10)
            if resp.ok:
                return True
        except Exception:
            pass
        if attempt < 2:
            time.sleep(2)
    return False

if not st.session_state.api_healthy:
    with st.spinner("Connecting to API..."):
        st.session_state.api_healthy = check_api_health()

if not st.session_state.api_healthy:
    st.error("❌ Cannot connect to API. Please ensure the API server is running.")
    st.info(f"Expected API at: {API_URL}")
    st.info("Start the API with: `python -m uvicorn backend.app:app --reload`")
    st.stop()

# Sidebar with controls
with st.sidebar:
    st.header("⚙️ Controls")
    st.caption(f"API: {API_URL}")
    
    st.markdown("---")
    st.subheader("🦠 Disease Filter")
    
    # Fetch available diseases (cached — won't re-hit API on every re-render)
    _disease_list = _api_get_diseases()
    available_diseases = ["All Diseases"] + _disease_list
    
    selected = st.selectbox(
        "Select Disease:",
        options=available_diseases,
        index=0,
        key="disease_selector",
    )
    
    # Store selected disease (None for "All Diseases")
    st.session_state.selected_disease = None if selected == "All Diseases" else selected
    
    if st.session_state.selected_disease:
        st.success(f"Filtering by: **{st.session_state.selected_disease}**")
    elif not _disease_list:
        st.warning("Could not load disease list")
    
    st.markdown("---")
    st.subheader("🗺️ Navigation")
    
    # Link to interactive heatmap
    heatmap_url = f"{API_URL}/ui/heatmap/"
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #5a67d8 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        margin-bottom: 1rem;
    ">
        <a href="{heatmap_url}" target="_blank" style="
            color: white;
            text-decoration: none;
            font-weight: 600;
        ">🗺️ Interactive Risk Heatmap →</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🚀 Run Full Pipeline")
    st.caption("One-click execution: Risk → Alerts → Forecasts")
    
    # Pipeline options
    reset_data = st.checkbox("Reset existing data", value=False, 
                             help="Delete existing risk scores, alerts, and forecasts for selected disease before running")
    horizon = st.number_input("Forecast horizon (days)", min_value=1, max_value=30, value=7)
    granularity = st.selectbox("Forecast granularity", options=["yearly", "monthly", "weekly"], index=1)
    
    # Get current disease filter for pipeline
    disease_param = st.session_state.selected_disease or "DENGUE"
    
    if st.button("▶️ Run Pipeline", type="primary", use_container_width=True):
        import time as time_module
        import threading
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        time_display = st.empty()
        
        # Get estimated time from session state (default 10s based on previous runs)
        estimated_time = st.session_state.get('last_pipeline_time', 10)
        
        # Start time tracking
        start_time = time_module.time()
        stop_timer = threading.Event()
        
        def update_timer():
            """Background thread to update elapsed time display."""
            while not stop_timer.is_set():
                elapsed = time_module.time() - start_time
                remaining = max(0, estimated_time - elapsed)
                if remaining > 0:
                    time_display.info(f"⏱️ Elapsed: {elapsed:.1f}s | Estimated remaining: ~{remaining:.0f}s")
                else:
                    time_display.info(f"⏱️ Elapsed: {elapsed:.1f}s | Almost done...")
                time_module.sleep(0.5)
        
        # Start timer thread
        timer_thread = threading.Thread(target=update_timer, daemon=True)
        timer_thread.start()
        
        try:
            # Step 1: Starting
            status_text.info("🚀 Step 1/3: Computing risk scores...")
            progress_bar.progress(10)
            
            # Build query parameters
            params = {
                "disease": disease_param,
                "reset": reset_data,
                "horizon": horizon,
                "granularity": granularity
            }
            
            # Update status to show we're calling the API
            status_text.info("🔄 Step 2/3: Generating alerts & forecasts...")
            progress_bar.progress(30)
            
            # Call one-click pipeline endpoint
            pipeline_response = requests.post(
                f"{API_URL}/pipeline/run",
                params=params,
                timeout=600
            )
            
            # Stop the timer
            stop_timer.set()
            elapsed_time = time_module.time() - start_time
            
            # Store this run time for future estimates
            st.session_state.last_pipeline_time = elapsed_time
            
            progress_bar.progress(90)
            
            if not pipeline_response.ok:
                st.error(f"❌ Pipeline failed: HTTP {pipeline_response.status_code}")
                if pipeline_response.text:
                    st.error(f"Details: {pipeline_response.text}")
                st.session_state.pipeline_status = "failed"
                time_display.error(f"⏱️ Failed after {elapsed_time:.1f}s")
            else:
                result = pipeline_response.json()
                progress_bar.progress(100)
                status_text.success("✓ Pipeline completed!")
                time_display.success(f"⏱️ Completed in {elapsed_time:.1f}s")
                
                # Show summary
                st.success("🎉 Pipeline completed successfully!")
                
                # Display results in columns
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Risk Scores", result["created"]["risk_scores"])
                with col2:
                    st.metric("Alerts", result["created"]["alerts"])
                with col3:
                    st.metric("Forecasts", result["created"]["forecasts"])
                
                # Show totals
                st.markdown("---")
                st.caption("**Total in Database:**")
                tot_col1, tot_col2, tot_col3 = st.columns(3)
                with tot_col1:
                    st.caption(f"📊 {result['total']['risk_scores']} risk scores")
                with tot_col2:
                    st.caption(f"⚠️ {result['total']['alerts']} alerts")
                with tot_col3:
                    st.caption(f"📈 {result['total']['forecasts']} forecasts")
                
                st.balloons()
                st.session_state.pipeline_status = "success"
                
                # Clear cached API data so the re-run fetches fresh results
                _api_get_hotspots.clear()
                _api_get_risk_latest.clear()
                _api_get_alerts.clear()
                _api_get_regions.clear()
                _api_get_forecast.clear()
                _api_get_evaluation.clear()
                
                # Force a rerun to refresh all data
                st.rerun()
            
        except requests.Timeout:
            stop_timer.set()
            elapsed_time = time_module.time() - start_time
            st.error("⏱️ Pipeline timeout - operations may still be running in background")
            time_display.error(f"⏱️ Timed out after {elapsed_time:.1f}s")
            st.session_state.pipeline_status = "timeout"
        except requests.ConnectionError:
            stop_timer.set()
            st.error("🔌 Connection error - is the API server running?")
            st.session_state.pipeline_status = "connection_error"
        except requests.RequestException as e:
            stop_timer.set()
            st.error(f"❌ Pipeline error: {str(e)}")
            st.session_state.pipeline_status = "error"
        except Exception as e:
            stop_timer.set()
            st.error(f"❌ Unexpected error: {str(e)}")
            st.session_state.pipeline_status = "error"
        finally:
            stop_timer.set()
            progress_bar.empty()
            status_text.empty()

st.markdown("---")

# Resolve disease filter once — used throughout all sections
disease_filter = st.session_state.selected_disease

# ===========================
# SECTION 1: HOTSPOTS
# ===========================
st.header("🔥 Hotspots")
st.caption("Regions with highest confirmed case counts")

with st.spinner("Loading hotspots..."):
    hotspots, hs_err = _api_get_hotspots(disease_filter)

if hs_err:
    st.error(f"Unable to reach API: {hs_err}")
elif hotspots is None:
    st.error("Failed to load hotspots")
elif hotspots:
    hotspot_df = pd.DataFrame(hotspots)
    if "confirmed_sum" in hotspot_df.columns:
        hotspot_df["confirmed_sum"] = hotspot_df["confirmed_sum"].apply(lambda x: f"{x:,}")
    if "deaths_sum" in hotspot_df.columns:
        hotspot_df["deaths_sum"] = hotspot_df["deaths_sum"].apply(lambda x: f"{x:,}")
    st.dataframe(hotspot_df, use_container_width=True, hide_index=True)
else:
    st.info("No hotspot data available")

st.markdown("---")

# ===========================
# SECTION 2: RISK HEATMAP / TOP HOTSPOTS
# (uses the same cached call as Section 3 — no duplicate fetch)
# ===========================
st.header("🗺️ Risk Heatmap / Top Hotspots")
st.caption("Top 10 regions ranked by risk score")

with st.spinner("Loading risk scores..."):
    risk_scores, risk_date, risk_err = _api_get_risk_latest(disease_filter)

if risk_err:
    st.error(f"Unable to reach API: {risk_err}")
elif not risk_scores:
    st.info("No risk score data available. Run the pipeline to generate risk scores.")
else:
    sorted_risks = sorted(risk_scores, key=lambda x: x.get("risk_score", 0), reverse=True)
    top_10 = sorted_risks[:10]
    
    st.info(f"📅 Risk assessment for: {risk_date} | Showing top {len(top_10)} regions")
    
    if PLOTLY_AVAILABLE and CUSTOM_COMPONENTS:
        fig = create_risk_heatmap(top_10, f"Top {len(top_10)} Regions by Risk Score")
        st.plotly_chart(fig, use_container_width=True, key="chart_risk_heatmap")
    else:
        import matplotlib.pyplot as plt
        _regions = [r.get("region_id", "Unknown") for r in top_10]
        _scores  = [r.get("risk_score", 0) for r in top_10]
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(_regions, _scores, color="#667eea")
        ax.set_xlabel("Risk Score")
        ax.set_xlim(0, 1.0)
        ax.grid(axis="x", alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig, clear_figure=True)
    
    st.subheader("📋 Risk Details")
    top10_rows = []
    for r in top_10:
        drivers = r.get("drivers") or []
        dt = ", ".join(drivers) if isinstance(drivers, list) else str(drivers)
        if len(dt) > 100:
            dt = dt[:97] + "..."
        top10_rows.append({
            "Region": r.get("region_id"),
            "Risk Score": round(r.get("risk_score", 0), 3),
            "Risk Level": r.get("risk_level"),
            "Drivers": dt,
        })
    st.dataframe(pd.DataFrame(top10_rows), use_container_width=True, hide_index=True)
    
    with st.expander("🎨 Risk Level Legend"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("🔴 **HIGH** - Score ≥ 0.7")
        with col2:
            st.markdown("🟠 **MEDIUM** - 0.4 ≤ Score < 0.7")
        with col3:
            st.markdown("🟢 **LOW** - Score < 0.4")

st.markdown("---")

# ===========================
# SECTION 3: RISK INTELLIGENCE
# (reuses the already-cached risk data — zero extra API calls)
# ===========================
st.header("📊 Risk Intelligence")
st.caption("Risk scores and drivers for all regions")

if risk_err:
    st.error(f"Unable to reach API: {risk_err}")
elif not risk_scores:
    st.info("No risk score data available")
else:
    st.info(f"📅 Latest risk assessment: {risk_date}")
    all_risk_rows = []
    for r in risk_scores:
        drivers = r.get("drivers") or []
        drivers_text = ", ".join(drivers) if isinstance(drivers, list) else str(drivers)
        all_risk_rows.append({
            "Region": r.get("region_id"),
            "Risk Score": round(r.get("risk_score", 0), 3),
            "Risk Level": r.get("risk_level"),
            "Drivers": drivers_text,
        })
    risk_df = pd.DataFrame(all_risk_rows)
    st.dataframe(risk_df, use_container_width=True, hide_index=True)
    disease_label = disease_filter if disease_filter else "ALL"
    _csv_download(risk_df, "📥 Download Risk Scores CSV", "risk_scores", disease_label, "download_risk")

st.markdown("---")

# ===========================
# SECTION 4: ALERTS FEED
# ===========================
st.header("🚨 Alerts Feed")
st.caption("Latest high-risk alerts from early warning system (limit: 20)")

with st.spinner("Loading alerts..."):
    alerts, alert_date, alerts_err = _api_get_alerts(disease_filter, limit=20)

if alerts_err:
    st.error(f"Unable to reach API: {alerts_err}")
elif alerts is None:
    st.error("Failed to load alerts")
elif alerts:
    st.info(f"📅 Showing {len(alerts)} alerts for {alert_date}")
    alert_df = pd.DataFrame(_format_alert_rows(alerts))
    st.dataframe(alert_df, use_container_width=True, hide_index=True)
    
    # Download: re-use the cached function with a higher limit
    export_alerts, _, _ = _api_get_alerts(disease_filter, limit=200)
    if export_alerts:
        export_df = pd.DataFrame(_format_alert_rows(export_alerts))
        disease_label = disease_filter if disease_filter else "ALL"
        _csv_download(
            export_df,
            f"📥 Download Alerts CSV ({len(export_alerts)} records)",
            "alerts", disease_label, "download_alerts",
        )
else:
    st.warning("No alerts found for the latest date")

st.markdown("---")

# ===========================
# SECTION 5: FORECAST VIEWER
# ===========================
st.header("📈 Forecast Viewer")
st.caption("7-day forecast with prediction bounds")

with st.spinner("Loading regions..."):
    region_options = _api_get_regions(disease_filter)

if not region_options:
    st.warning("No regions available. Please run the pipeline first.")
else:
    selected_region = st.selectbox("Select Region", region_options, key="forecast_region")
    
    with st.spinner(f"Loading forecast for {selected_region}..."):
        forecasts, fc_err = _api_get_forecast(selected_region, disease_filter, horizon=7)
    
    if fc_err:
        st.error(f"Unable to reach API: {fc_err}")
    elif not forecasts:
        st.warning(f"No forecast data available for {selected_region}")
    else:
        forecast_df = pd.DataFrame(forecasts)
        forecast_df["date"] = pd.to_datetime(forecast_df["date"])
        
        if PLOTLY_AVAILABLE and CUSTOM_COMPONENTS:
            fig = create_forecast_chart(forecasts, selected_region)
            st.plotly_chart(fig, use_container_width=True, key="chart_forecast")
        else:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(forecast_df["date"], forecast_df["pred_mean"],
                    label="Predicted", color="#667eea", marker="o", linewidth=2)
            ax.fill_between(forecast_df["date"], forecast_df["pred_lower"],
                            forecast_df["pred_upper"], alpha=0.2, color="#667eea")
            ax.set_xlabel("Date")
            ax.set_ylabel("Predicted Cases")
            ax.set_title(f"7-Day Forecast for {selected_region}")
            ax.legend()
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig, clear_figure=True)
        
        with st.expander("📋 View Forecast Data"):
            forecast_table = forecast_df[["date", "pred_mean", "pred_lower", "pred_upper"]].copy()
            forecast_table["date"] = forecast_table["date"].dt.strftime("%Y-%m-%d")
            forecast_table["pred_mean"]  = forecast_table["pred_mean"].round(1)
            forecast_table["pred_lower"] = forecast_table["pred_lower"].round(1)
            forecast_table["pred_upper"] = forecast_table["pred_upper"].round(1)
            st.dataframe(forecast_table, use_container_width=True, hide_index=True)
        
        disease_label = disease_filter if disease_filter else "ALL"
        _csv_download(
            forecast_table,
            f"📥 Download Forecast CSV for {selected_region}",
            f"forecast_{selected_region}", disease_label, "download_forecast",
        )
        
        # Model Evaluation
        st.subheader("📐 Model Evaluation")
        st.caption("Forecast accuracy metrics (MAE = Mean Absolute Error, MAPE = Mean Absolute Percentage Error)")
        
        with st.spinner("Loading evaluation metrics..."):
            eval_data, eval_err = _api_get_evaluation(selected_region, horizon=7)
        
        if eval_err:
            st.warning(f"Evaluation unavailable: {eval_err}")
        elif eval_data:
            col1, col2, col3 = st.columns(3)
            with col1:
                mae = eval_data.get("mae")
                st.metric("MAE", f"{mae:.2f}" if mae is not None else "N/A",
                          help="Mean Absolute Error - Lower is better")
            with col2:
                mape = eval_data.get("mape")
                st.metric("MAPE", f"{mape:.2f}%" if mape is not None else "N/A",
                          help="Mean Absolute Percentage Error - Lower is better")
            with col3:
                st.metric("Data Points", eval_data.get("points_compared", 0),
                          help="Number of forecast points compared with actuals")
            with st.expander("ℹ️ Evaluation Details"):
                st.json(eval_data)
        else:
            st.warning("No evaluation data returned")

