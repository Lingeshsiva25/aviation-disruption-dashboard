import streamlit as st
import pandas as pd
import plotly.express as px
import time

st.set_page_config(
    page_title="Aviation Disruption Intelligence Center",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS - ENTERPRISE LOOK
# =========================================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0b1220, #111827);
        color: #f8fafc;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    section[data-testid="stSidebar"] {
        background: #0f172a;
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    .logo-box {
        display: flex;
        align-items: center;
        gap: 14px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 16px 18px;
        margin-bottom: 18px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.25);
    }

    .logo-icon {
        font-size: 2rem;
        background: linear-gradient(135deg, #38bdf8, #6366f1);
        border-radius: 14px;
        padding: 10px 14px;
    }

    .logo-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
    }

    .logo-subtitle {
        font-size: 0.92rem;
        color: #94a3b8;
        margin: 0;
    }

    .page-title {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.2rem;
    }

    .page-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 1rem;
    }

    .kpi-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.22);
        min-height: 120px;
    }

    .kpi-label {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-bottom: 10px;
    }

    .kpi-value {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 700;
        line-height: 1.1;
    }

    .kpi-small {
        color: #38bdf8;
        font-size: 0.85rem;
        margin-top: 8px;
    }

    .panel-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }

    .section-title {
        color: #ffffff;
        font-size: 1.15rem;
        font-weight: 600;
        margin-bottom: 10px;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.08);
        background: rgba(255,255,255,0.05);
        color: white;
        font-weight: 600;
        padding: 0.65rem 0.8rem;
    }

    div.stButton > button:hover {
        border: 1px solid rgba(56,189,248,0.7);
        color: #38bdf8;
    }

    .insight-box {
        background: rgba(56,189,248,0.10);
        border: 1px solid rgba(56,189,248,0.22);
        padding: 14px;
        border-radius: 14px;
        color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():
    cancellations = pd.read_csv("flight_cancellations.csv")
    reroutes = pd.read_csv("flight_reroutes.csv")
    airline_losses = pd.read_csv("airline_losses.csv")
    airline_losses_est = pd.read_csv("airline_losses_estimate.csv")
    disruptions = pd.read_csv("airport_disruptions.csv")
    airspace = pd.read_csv("airspace_closures.csv")
    conflict = pd.read_csv("conflict_events.csv")

    for df, cols in [
        (cancellations, ["date"]),
        (reroutes, ["date"]),
        (disruptions, ["date"]),
        (conflict, ["date"]),
        (airspace, ["closure_start_date", "closure_end_date"])
    ]:
        for col in cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

    return cancellations, reroutes, airline_losses, airline_losses_est, disruptions, airspace, conflict


df_cancel, df_reroute, df_loss, df_loss_est, df_disrupt, df_airspace, df_conflict = load_data()

# =========================================================
# SESSION STATE FOR NAVIGATION
# =========================================================
if "page" not in st.session_state:
    st.session_state.page = "Executive Overview"

# =========================================================
# SIDEBAR - LOGO + NAVIGATION
# =========================================================
st.sidebar.markdown("""
<div class="logo-box">
    <div class="logo-icon">✈️</div>
    <div>
        <p class="logo-title">Aviation BI</p>
        <p class="logo-subtitle">Disruption Intelligence Suite</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### Navigation")

if st.sidebar.button("Executive Overview"):
    st.session_state.page = "Executive Overview"
if st.sidebar.button("Global Risk Map"):
    st.session_state.page = "Global Risk Map"
if st.sidebar.button("Flight Operations"):
    st.session_state.page = "Flight Operations"
if st.sidebar.button("Financial Impact"):
    st.session_state.page = "Financial Impact"
if st.sidebar.button("Airport Disruptions"):
    st.session_state.page = "Airport Disruptions"
if st.sidebar.button("Conflict Monitoring"):
    st.session_state.page = "Conflict Monitoring"
if st.sidebar.button("Data Export"):
    st.session_state.page = "Data Export"

st.sidebar.markdown("---")
st.sidebar.markdown("### Filters")

# Date range
available_dates = []
for df in [df_cancel, df_reroute, df_disrupt, df_conflict]:
    if "date" in df.columns and df["date"].notna().any():
        available_dates.extend(df["date"].dropna().tolist())

if available_dates:
    min_date = min(available_dates).date()
    max_date = max(available_dates).date()
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
else:
    date_range = None

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
else:
    start_date = None
    end_date = None

if "region" in df_loss.columns:
    region_options = sorted(df_loss["region"].dropna().unique())
    selected_regions = st.sidebar.multiselect(
        "Regions",
        options=region_options,
        default=region_options
    )
else:
    selected_regions = []

if "severity" in df_conflict.columns:
    severity_options = sorted(df_conflict["severity"].dropna().unique())
    selected_severity = st.sidebar.multiselect(
        "Conflict Severity",
        options=severity_options,
        default=severity_options
    )
else:
    selected_severity = []

# =========================================================
# FILTER DATA
# =========================================================
cancel_f = df_cancel.copy()
reroute_f = df_reroute.copy()
disrupt_f = df_disrupt.copy()
conflict_f = df_conflict.copy()
loss_f = df_loss.copy()

if start_date is not None and end_date is not None:
    if "date" in cancel_f.columns:
        cancel_f = cancel_f[(cancel_f["date"] >= start_date) & (cancel_f["date"] <= end_date)]
    if "date" in reroute_f.columns:
        reroute_f = reroute_f[(reroute_f["date"] >= start_date) & (reroute_f["date"] <= end_date)]
    if "date" in disrupt_f.columns:
        disrupt_f = disrupt_f[(disrupt_f["date"] >= start_date) & (disrupt_f["date"] <= end_date)]
    if "date" in conflict_f.columns:
        conflict_f = conflict_f[(conflict_f["date"] >= start_date) & (conflict_f["date"] <= end_date)]

if selected_regions and "region" in loss_f.columns:
    loss_f = loss_f[loss_f["region"].isin(selected_regions)]

if selected_severity and "severity" in conflict_f.columns:
    conflict_f = conflict_f[conflict_f["severity"].isin(selected_severity)]

# =========================================================
# KPI VALUES
# =========================================================
total_cancellations = len(cancel_f)
total_reroutes = len(reroute_f)
total_conflicts = len(conflict_f)
total_airports = disrupt_f["airport_name"].nunique() if "airport_name" in disrupt_f.columns else len(disrupt_f)

if "estimated_loss_usd" in loss_f.columns:
    total_loss = float(loss_f["estimated_loss_usd"].sum())
else:
    total_loss = 0.0

if "revenue_loss_pct" in loss_f.columns and len(loss_f) > 0:
    avg_loss_pct = float(loss_f["revenue_loss_pct"].mean())
else:
    avg_loss_pct = 0.0

risk_score = min(
    100,
    (total_cancellations * 0.06) +
    (total_reroutes * 0.08) +
    (total_conflicts * 2.5) +
    (avg_loss_pct * 1.3)
)

if risk_score >= 75:
    risk_level = "Critical"
elif risk_score >= 50:
    risk_level = "High"
elif risk_score >= 30:
    risk_level = "Moderate"
else:
    risk_level = "Low"

# =========================================================
# HELPER - ANIMATED KPI
# =========================================================
def animated_kpi(label, value, prefix="", suffix="", note=""):
    placeholder = st.empty()
    try:
        target = int(value)
        steps = min(25, max(5, target // 5 if target > 0 else 5))
        for i in range(0, target + 1, max(1, target // steps if target > 0 else 1)):
            placeholder.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{prefix}{i:,}{suffix}</div>
                <div class="kpi-small">{note}</div>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.015)
        placeholder.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{prefix}{target:,}{suffix}</div>
            <div class="kpi-small">{note}</div>
        </div>
        """, unsafe_allow_html=True)
    except:
        placeholder.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{prefix}{value}{suffix}</div>
            <div class="kpi-small">{note}</div>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="page-title">Aviation Disruption Intelligence Center</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="page-subtitle">Current workspace: <b>{st.session_state.page}</b> | Enterprise monitoring of operational disruptions, conflict-driven aviation risk, and financial loss exposure.</div>',
    unsafe_allow_html=True
)

# =========================================================
# PAGE: EXECUTIVE OVERVIEW
# =========================================================
if st.session_state.page == "Executive Overview":
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        animated_kpi("Cancellations", total_cancellations, note="Filtered operations")
    with c2:
        animated_kpi("Reroutes", total_reroutes, note="Route deviation events")
    with c3:
        animated_kpi("Conflict Events", total_conflicts, note="Monitored incidents")
    with c4:
        animated_kpi("Loss Exposure", int(total_loss), prefix="$", note="Estimated financial impact")
    with c5:
        animated_kpi("Risk Score", int(risk_score), suffix="/100", note=risk_level)

    left, right = st.columns([2, 1])

    with left:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Global Aviation Impact Map</div>', unsafe_allow_html=True)

        map_df = None
        if "country" in loss_f.columns and "estimated_loss_usd" in loss_f.columns:
            map_df = loss_f.groupby("country", as_index=False)["estimated_loss_usd"].sum()
            fig_map = px.choropleth(
                map_df,
                locations="country",
                locationmode="country names",
                color="estimated_loss_usd",
                hover_name="country",
                color_continuous_scale="Reds"
            )
            fig_map.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                geo=dict(bgcolor="rgba(0,0,0,0)", showframe=False, showcoastlines=True),
                margin=dict(l=0, r=0, t=20, b=0),
                height=480
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("Country-based loss data not available for the map.")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Executive Insight</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="insight-box">
            <b>Current Risk Level:</b> {risk_level}<br><br>
            <b>Key Signals:</b><br>
            • {total_cancellations:,} cancellations observed<br>
            • {total_reroutes:,} reroutes registered<br>
            • {total_conflicts:,} conflict events tracked<br>
            • ${total_loss:,.0f} estimated loss exposure<br><br>
            This dashboard highlights disruption intensity across routes, airspace, airports, and airline financial performance.
        </div>
        """, unsafe_allow_html=True)
        st.progress(int(risk_score))
        st.markdown('</div>', unsafe_allow_html=True)

    b1, b2 = st.columns(2)

    with b1:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Top Airlines by Estimated Loss</div>', unsafe_allow_html=True)
        if {"airline", "estimated_loss_usd"}.issubset(loss_f.columns):
            top_loss = loss_f.groupby("airline", as_index=False)["estimated_loss_usd"].sum().sort_values(
                "estimated_loss_usd", ascending=False
            ).head(10)
            fig = px.bar(
                top_loss,
                x="estimated_loss_usd",
                y="airline",
                orientation="h",
                color="estimated_loss_usd",
                color_continuous_scale="Reds"
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                yaxis=dict(categoryorder="total ascending")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Airline loss columns not found.")
        st.markdown('</div>', unsafe_allow_html=True)

    with b2:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Loss Distribution by Region</div>', unsafe_allow_html=True)
        if {"region", "estimated_loss_usd"}.issubset(loss_f.columns):
            region_df = loss_f.groupby("region", as_index=False)["estimated_loss_usd"].sum()
            fig = px.pie(region_df, names="region", values="estimated_loss_usd", hole=0.5)
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Region-based loss data not available.")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# PAGE: GLOBAL RISK MAP
# =========================================================
elif st.session_state.page == "Global Risk Map":
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Interactive Global Map</div>', unsafe_allow_html=True)

    layer = st.radio(
        "Select map layer",
        ["Estimated Airline Loss", "Airspace Closures", "Airport Disruptions"],
        horizontal=True
    )

    if layer == "Estimated Airline Loss" and {"country", "estimated_loss_usd"}.issubset(loss_f.columns):
        map_df = loss_f.groupby("country", as_index=False)["estimated_loss_usd"].sum()
        fig = px.choropleth(
            map_df,
            locations="country",
            locationmode="country names",
            color="estimated_loss_usd",
            hover_name="country",
            color_continuous_scale="Reds"
        )
    elif layer == "Airspace Closures" and {"country", "flights_affected"}.issubset(df_airspace.columns):
        map_df = df_airspace.groupby("country", as_index=False)["flights_affected"].sum()
        fig = px.choropleth(
            map_df,
            locations="country",
            locationmode="country names",
            color="flights_affected",
            hover_name="country",
            color_continuous_scale="Oranges"
        )
    elif layer == "Airport Disruptions" and {"country", "flights_affected"}.issubset(disrupt_f.columns):
        map_df = disrupt_f.groupby("country", as_index=False)["flights_affected"].sum()
        fig = px.choropleth(
            map_df,
            locations="country",
            locationmode="country names",
            color="flights_affected",
            hover_name="country",
            color_continuous_scale="Blues"
        )
    else:
        fig = None
        st.warning("Required country-level columns were not found for this layer.")

    if fig is not None:
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            geo=dict(bgcolor="rgba(0,0,0,0)", showframe=False, showcoastlines=True),
            margin=dict(l=0, r=0, t=20, b=0),
            height=560
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# PAGE: FLIGHT OPERATIONS
# =========================================================
elif st.session_state.page == "Flight Operations":
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Top Airlines by Cancellations</div>', unsafe_allow_html=True)
        if "airline" in cancel_f.columns:
            airline_cancel = cancel_f.groupby("airline", as_index=False).size().rename(columns={"size": "cancellations"})
            airline_cancel = airline_cancel.sort_values("cancellations", ascending=False).head(12)
            fig = px.bar(
                airline_cancel,
                x="airline",
                y="cancellations",
                color="cancellations",
                color_continuous_scale="Reds"
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                xaxis_tickangle=-35
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Airline column not found in cancellation data.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Average Delay Hours by Airline</div>', unsafe_allow_html=True)
        if {"airline", "delay_hours"}.issubset(reroute_f.columns):
            route_delay = reroute_f.groupby("airline", as_index=False)["delay_hours"].mean().sort_values(
                "delay_hours", ascending=False
            ).head(12)
            fig = px.bar(
                route_delay,
                x="airline",
                y="delay_hours",
                color="delay_hours",
                color_continuous_scale="Blues"
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                xaxis_tickangle=-35
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Delay data not available.")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# PAGE: FINANCIAL IMPACT
# =========================================================
elif st.session_state.page == "Financial Impact":
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Estimated Airline Loss by Airline</div>', unsafe_allow_html=True)
        if {"airline", "estimated_loss_usd"}.issubset(loss_f.columns):
            top_loss = loss_f.groupby("airline", as_index=False)["estimated_loss_usd"].sum().sort_values(
                "estimated_loss_usd", ascending=False
            ).head(12)
            fig = px.bar(
                top_loss,
                x="estimated_loss_usd",
                y="airline",
                orientation="h",
                color="estimated_loss_usd",
                color_continuous_scale="Reds"
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                yaxis=dict(categoryorder="total ascending")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Estimated loss columns not found.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Revenue Loss Percentage</div>', unsafe_allow_html=True)
        if {"airline", "revenue_loss_pct"}.issubset(loss_f.columns):
            pct_df = loss_f.groupby("airline", as_index=False)["revenue_loss_pct"].mean().sort_values(
                "revenue_loss_pct", ascending=False
            ).head(12)
            fig = px.bar(
                pct_df,
                x="airline",
                y="revenue_loss_pct",
                color="revenue_loss_pct",
                color_continuous_scale="Oranges"
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                xaxis_tickangle=-35
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Revenue loss % data not available.")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# PAGE: AIRPORT DISRUPTIONS
# =========================================================
elif st.session_state.page == "Airport Disruptions":
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Top Disrupted Airports</div>', unsafe_allow_html=True)
        if {"airport_name", "flights_affected"}.issubset(disrupt_f.columns):
            top_airports = disrupt_f.groupby("airport_name", as_index=False)["flights_affected"].sum().sort_values(
                "flights_affected", ascending=False
            ).head(10)
            fig = px.bar(
                top_airports,
                x="flights_affected",
                y="airport_name",
                orientation="h",
                color="flights_affected",
                color_continuous_scale="Blues"
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                yaxis=dict(categoryorder="total ascending")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Airport disruption columns not found.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Severity Level Impact</div>', unsafe_allow_html=True)
        if {"severity_level", "flights_affected"}.issubset(disrupt_f.columns):
            sev_df = disrupt_f.groupby("severity_level", as_index=False)["flights_affected"].sum()
            fig = px.bar(
                sev_df,
                x="severity_level",
                y="flights_affected",
                color="flights_affected",
                color_continuous_scale="Tealgrn"
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Severity-level data not available.")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# PAGE: CONFLICT MONITORING
# =========================================================
elif st.session_state.page == "Conflict Monitoring":
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Conflict Timeline</div>', unsafe_allow_html=True)

    if {"date", "severity"}.issubset(conflict_f.columns):
        timeline = conflict_f.groupby(["date", "severity"], as_index=False).size().rename(columns={"size": "events"})
        fig = px.line(
            timeline,
            x="date",
            y="events",
            color="severity",
            markers=True
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Conflict date/severity columns not found.")

    st.markdown('</div>', unsafe_allow_html=True)
    st.dataframe(conflict_f, use_container_width=True)

# =========================================================
# PAGE: DATA EXPORT
# =========================================================
elif st.session_state.page == "Data Export":
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Download Filtered Data</div>', unsafe_allow_html=True)

    export_choice = st.selectbox(
        "Choose dataset",
        [
            "Filtered Cancellations",
            "Filtered Reroutes",
            "Filtered Airport Disruptions",
            "Filtered Conflict Events",
            "Filtered Airline Losses"
        ]
    )

    if export_choice == "Filtered Cancellations":
        export_df = cancel_f
        file_name = "filtered_cancellations.csv"
    elif export_choice == "Filtered Reroutes":
        export_df = reroute_f
        file_name = "filtered_reroutes.csv"
    elif export_choice == "Filtered Airport Disruptions":
        export_df = disrupt_f
        file_name = "filtered_airport_disruptions.csv"
    elif export_choice == "Filtered Conflict Events":
        export_df = conflict_f
        file_name = "filtered_conflict_events.csv"
    else:
        export_df = loss_f
        file_name = "filtered_airline_losses.csv"

    st.download_button(
        label="Download CSV",
        data=export_df.to_csv(index=False).encode("utf-8"),
        file_name=file_name,
        mime="text/csv"
    )

    st.dataframe(export_df.head(50), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)