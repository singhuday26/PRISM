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
    
    # Fetch available diseases
    try:
        diseases_resp = requests.get(f"{API_URL}/regions/diseases", timeout=30)
        if diseases_resp.ok:
            diseases_data = diseases_resp.json()
            available_diseases = ["All Diseases"] + diseases_data.get("diseases", [])
            
            selected = st.selectbox(
                "Select Disease:",
                options=available_diseases,
                index=0,
                key="disease_selector"
            )
            
            # Store selected disease (None for "All Diseases")
            st.session_state.selected_disease = None if selected == "All Diseases" else selected
            
            if st.session_state.selected_disease:
                st.success(f"Filtering by: **{st.session_state.selected_disease}**")
        else:
            st.warning("Could not load disease list")
            st.session_state.selected_disease = None
    except Exception as e:
        st.error(f"Error loading diseases: {str(e)}")
        st.session_state.selected_disease = None
    
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

# Build query parameter for disease filter
disease_filter = st.session_state.selected_disease
disease_query_param = f"?disease={disease_filter}" if disease_filter else ""

# ===========================
# SECTION 1: HOTSPOTS
# ===========================
st.header("🔥 Hotspots")
st.caption("Regions with highest confirmed case counts")

try:
    hotspot_resp = requests.get(f"{API_URL}/hotspots{disease_query_param}", timeout=30)
    if hotspot_resp.ok:
        data = hotspot_resp.json()
        hotspots = data.get("hotspots", [])
        
        if hotspots:
            hotspot_df = pd.DataFrame(hotspots)
            
            # Format columns for better display
            if "confirmed_sum" in hotspot_df.columns:
                hotspot_df["confirmed_sum"] = hotspot_df["confirmed_sum"].apply(lambda x: f"{x:,}")
            if "deaths_sum" in hotspot_df.columns:
                hotspot_df["deaths_sum"] = hotspot_df["deaths_sum"].apply(lambda x: f"{x:,}")
            
            st.dataframe(hotspot_df, use_container_width=True, hide_index=True)
        else:
            st.info("No hotspot data available")
    else:
        st.error(f"Failed to load hotspots: HTTP {hotspot_resp.status_code}")
except requests.RequestException as e:
    st.error(f"Unable to reach API: {str(e)}")
except Exception as e:
    st.error(f"Error displaying hotspots: {str(e)}")

st.markdown("---")

# ===========================
# SECTION 2: RISK HEATMAP / TOP HOTSPOTS
# ===========================
st.header("🗺️ Risk Heatmap / Top Hotspots")
st.caption("Top 10 regions ranked by risk score")

try:
    risk_heatmap_resp = requests.get(f"{API_URL}/risk/latest{disease_query_param}", timeout=30)
    if risk_heatmap_resp.ok:
        data = risk_heatmap_resp.json()
        risk_scores = data.get("risk_scores", [])
        risk_date = data.get("date")
        
        if risk_scores:
            # Sort by risk_score descending and take top 10
            sorted_risks = sorted(risk_scores, key=lambda x: x.get("risk_score", 0), reverse=True)
            top_10 = sorted_risks[:10]  # Works even if <10 regions
            
            if top_10:
                st.info(f"📅 Risk assessment for: {risk_date} | Showing top {len(top_10)} regions")
                
                # Use Plotly if available, otherwise fallback
                if PLOTLY_AVAILABLE and CUSTOM_COMPONENTS:
                    fig = create_risk_heatmap(top_10, f"Top {len(top_10)} Regions by Risk Score")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Fallback to simple bar display
                    import matplotlib.pyplot as plt
                    regions = [r.get("region_id", "Unknown") for r in top_10]
                    scores = [r.get("risk_score", 0) for r in top_10]
                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    bars = ax.barh(regions, scores, color='#667eea')
                    ax.set_xlabel("Risk Score")
                    ax.set_xlim(0, 1.0)
                    ax.grid(axis='x', alpha=0.3)
                    plt.tight_layout()
                    st.pyplot(fig)
                
                # Create detailed table
                st.subheader("📋 Risk Details")
                table_rows = []
                for r in top_10:
                    drivers = r.get("drivers") or []
                    drivers_text = ", ".join(drivers) if isinstance(drivers, list) else str(drivers)
                    
                    # Truncate long drivers text for better display
                    if len(drivers_text) > 100:
                        drivers_text = drivers_text[:97] + "..."
                    
                    table_rows.append({
                        "Region": r.get("region_id"),
                        "Risk Score": round(r.get("risk_score", 0), 3),
                        "Risk Level": r.get("risk_level"),
                        "Drivers": drivers_text,
                    })
                
                risk_table_df = pd.DataFrame(table_rows)
                st.dataframe(risk_table_df, use_container_width=True, hide_index=True)
                
                # Add color legend
                with st.expander("🎨 Risk Level Legend"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown("🔴 **HIGH** - Score ≥ 0.7")
                    with col2:
                        st.markdown("🟠 **MEDIUM** - 0.4 ≤ Score < 0.7")
                    with col3:
                        st.markdown("🟢 **LOW** - Score < 0.4")
            else:
                st.info("No risk data available for visualization")
        else:
            st.info("No risk score data available. Run the pipeline to generate risk scores.")
    else:
        st.error(f"Failed to load risk scores: HTTP {risk_heatmap_resp.status_code}")
except requests.RequestException as e:
    st.error(f"Unable to reach API: {str(e)}")
except Exception as e:
    st.error(f"Error displaying risk heatmap: {str(e)}")

st.markdown("---")

# ===========================
# SECTION 3: RISK INTELLIGENCE
# ===========================
st.header("📊 Risk Intelligence")
st.caption("Risk scores and drivers for all regions")

try:
    risk_resp = requests.get(f"{API_URL}/risk/latest{disease_query_param}", timeout=30)
    if risk_resp.ok:
        data = risk_resp.json()
        risk_scores = data.get("risk_scores", [])
        risk_date = data.get("date")
        
        if risk_scores:
            st.info(f"📅 Latest risk assessment: {risk_date}")
            
            # Build table with drivers
            table_rows = []
            for r in risk_scores:
                drivers = r.get("drivers") or []
                drivers_text = ", ".join(drivers) if isinstance(drivers, list) else str(drivers)
                
                table_rows.append({
                    "Region": r.get("region_id"),
                    "Risk Score": round(r.get("risk_score", 0), 3),
                    "Risk Level": r.get("risk_level"),
                    "Drivers": drivers_text,
                })
            
            risk_df = pd.DataFrame(table_rows)
            st.dataframe(risk_df, use_container_width=True, hide_index=True)
            
            disease_label = disease_filter if disease_filter else "ALL"
            _csv_download(risk_df, "📥 Download Risk Scores CSV", "risk_scores", disease_label, "download_risk")
        else:
            st.info("No risk score data available")
    else:
        st.error(f"Failed to load risk scores: HTTP {risk_resp.status_code}")
except requests.RequestException as e:
    st.error(f"Unable to reach API: {str(e)}")
except Exception as e:
    st.error(f"Error displaying risk intelligence: {str(e)}")

st.markdown("---")

# ===========================
# SECTION 4: ALERTS FEED
# ===========================
st.header("🚨 Alerts Feed")
st.caption("Latest high-risk alerts from early warning system (limit: 20)")

try:
    alerts_resp = requests.get(f"{API_URL}/alerts/latest?limit=20{'' if not disease_filter else '&disease=' + disease_filter}", timeout=30)
    if alerts_resp.ok:
        data = alerts_resp.json()
        alerts = data.get("alerts", [])
        alert_date = data.get("date")
        
        if alerts:
            st.info(f"📅 Showing {len(alerts)} alerts for {alert_date}")
            
            alert_df = pd.DataFrame(_format_alert_rows(alerts))
            st.dataframe(alert_df, use_container_width=True, hide_index=True)
            
            # Download button — fetch up to 200 alerts for export
            try:
                export_url = f"{API_URL}/alerts/latest?limit=200"
                if disease_filter:
                    export_url += f"&disease={disease_filter}"
                export_resp = requests.get(export_url, timeout=60)
                if export_resp.ok:
                    export_alerts = export_resp.json().get("alerts", [])
                    if export_alerts:
                        export_df = pd.DataFrame(_format_alert_rows(export_alerts))
                        disease_label = disease_filter if disease_filter else "ALL"
                        _csv_download(
                            export_df,
                            f"📥 Download Alerts CSV ({len(export_alerts)} records)",
                            "alerts", disease_label, "download_alerts",
                        )
            except Exception as e:
                st.warning(f"Unable to prepare download: {str(e)}")
        else:
            st.warning("No alerts found for the latest date")
    else:
        st.error(f"Failed to load alerts: HTTP {alerts_resp.status_code}")
except requests.RequestException as e:
    st.error(f"Unable to reach API: {str(e)}")
except Exception as e:
    st.error(f"Error displaying alerts: {str(e)}")

st.markdown("---")

# ===========================
# SECTION 5: FORECAST VIEWER
# ===========================
st.header("📈 Forecast Viewer")
st.caption("7-day forecast with prediction bounds")

try:
    # Get regions for dropdown (filtered by disease)
    regions_resp = requests.get(f"{API_URL}/regions{disease_query_param}", timeout=30)
    region_options = []
    
    if regions_resp.ok:
        regions = regions_resp.json().get("regions", [])
        region_options = [r.get("region_id") for r in regions if r.get("region_id")]
    
    if region_options:
        selected_region = st.selectbox("Select Region", region_options, key="forecast_region")
        
        try:
            forecast_url = f"{API_URL}/forecasts/latest?region_id={selected_region}&horizon=7"
            if disease_filter:
                forecast_url += f"&disease={disease_filter}"
            
            forecast_resp = requests.get(forecast_url, timeout=60)
            
            if forecast_resp.ok:
                data = forecast_resp.json()
                forecasts = data.get("forecasts", [])
                
                if forecasts:
                    forecast_df = pd.DataFrame(forecasts)
                    forecast_df["date"] = pd.to_datetime(forecast_df["date"])
                    
                    # Create forecast plot with Plotly
                    if PLOTLY_AVAILABLE and CUSTOM_COMPONENTS:
                        fig = create_forecast_chart(forecasts, selected_region)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        # Fallback to matplotlib
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
                        st.pyplot(fig)
                    
                    # Show forecast data table
                    with st.expander("📋 View Forecast Data"):
                        forecast_table = forecast_df[["date", "pred_mean", "pred_lower", "pred_upper"]].copy()
                        forecast_table["date"] = forecast_table["date"].dt.strftime("%Y-%m-%d")
                        forecast_table["pred_mean"] = forecast_table["pred_mean"].round(1)
                        forecast_table["pred_lower"] = forecast_table["pred_lower"].round(1)
                        forecast_table["pred_upper"] = forecast_table["pred_upper"].round(1)
                        st.dataframe(forecast_table, use_container_width=True, hide_index=True)
                    
                    # Download button for Forecast CSV
                    disease_label = disease_filter if disease_filter else "ALL"
                    _csv_download(
                        forecast_table,
                        f"📥 Download Forecast CSV for {selected_region}",
                        f"forecast_{selected_region}", disease_label, "download_forecast",
                    )
                    
                    # Model Evaluation Section
                    st.subheader("📐 Model Evaluation")
                    st.caption("Forecast accuracy metrics (MAE = Mean Absolute Error, MAPE = Mean Absolute Percentage Error)")
                    
                    try:
                        eval_resp = requests.get(
                            f"{API_URL}/evaluation/forecast?region_id={selected_region}&horizon=7",
                            timeout=60
                        )
                        
                        if eval_resp.ok:
                            eval_data = eval_resp.json()
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                mae = eval_data.get("mae")
                                if mae is not None:
                                    st.metric("MAE", f"{mae:.2f}", help="Mean Absolute Error - Lower is better")
                                else:
                                    st.metric("MAE", "N/A", help="Not enough data to compute")
                            
                            with col2:
                                mape = eval_data.get("mape")
                                if mape is not None:
                                    st.metric("MAPE", f"{mape:.2f}%", help="Mean Absolute Percentage Error - Lower is better")
                                else:
                                    st.metric("MAPE", "N/A", help="Not enough data to compute")
                            
                            with col3:
                                points = eval_data.get("points_compared", 0)
                                st.metric("Data Points", points, help="Number of forecast points compared with actuals")
                            
                            # Show additional info in expander
                            with st.expander("ℹ️ Evaluation Details"):
                                st.json(eval_data)
                        else:
                            st.warning(f"Evaluation unavailable: HTTP {eval_resp.status_code}")
                    except requests.RequestException as e:
                        st.warning(f"Unable to fetch evaluation: {str(e)}")
                    except Exception as e:
                        st.warning(f"Error displaying evaluation: {str(e)}")
                    
                else:
                    st.warning(f"No forecast data available for {selected_region}")
            else:
                st.error(f"Failed to load forecasts: HTTP {forecast_resp.status_code}")
        except requests.RequestException as e:
            st.error(f"Unable to reach API: {str(e)}")
        except Exception as e:
            st.error(f"Error displaying forecast: {str(e)}")
    else:
        st.warning("No regions available. Please run the pipeline first.")
        
except requests.RequestException as e:
    st.error(f"Unable to load regions: {str(e)}")
except Exception as e:
    st.error(f"Error in forecast viewer: {str(e)}")

