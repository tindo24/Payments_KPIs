import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Payments Analytics | Togetherwork",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0f1117;
    color: #e8e8e8;
  }
  .main { background-color: #0f1117; }
  .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: #161b27;
    border-right: 1px solid #2a2f3d;
  }
  section[data-testid="stSidebar"] * { color: #c8cdd8 !important; }

  /* KPI Cards */
  .kpi-card {
    background: linear-gradient(135deg, #1a2035 0%, #1e2640 100%);
    border: 1px solid #2a3050;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.5rem;
    transition: border-color 0.2s;
  }
  .kpi-card:hover { border-color: #4a6fa5; }
  .kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #7a8aa0;
    margin-bottom: 0.3rem;
  }
  .kpi-value {
    font-family: 'DM Serif Display', serif;
    font-size: 1.9rem;
    color: #e8eaf6;
    line-height: 1.1;
  }
  .kpi-delta-pos { font-size: 0.78rem; color: #4caf87; font-weight: 500; }
  .kpi-delta-neg { font-size: 0.78rem; color: #e05c6a; font-weight: 500; }

  /* Section headers */
  .section-header {
    font-family: 'DM Serif Display', serif;
    font-size: 1.3rem;
    color: #c8d8f0;
    border-left: 3px solid #4a6fa5;
    padding-left: 0.75rem;
    margin: 1.5rem 0 0.8rem 0;
  }

  /* Chart containers */
  .chart-container {
    background: #161b27;
    border: 1px solid #2a3050;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
  }

  /* Dashboard title */
  .dash-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #c8d8f0;
    margin-bottom: 0;
  }
  .dash-subtitle {
    font-size: 0.85rem;
    color: #5a6a80;
    margin-top: 0.1rem;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    background: #161b27;
    border-radius: 8px;
    gap: 4px;
    padding: 4px;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #7a8aa0;
    border-radius: 6px;
    font-size: 0.82rem;
    font-weight: 500;
    letter-spacing: 0.03em;
  }
  .stTabs [aria-selected="true"] {
    background: #2a3a5c !important;
    color: #c8d8f0 !important;
  }
  div[data-testid="stMetricValue"] { font-family: 'DM Serif Display', serif; }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("payments_dataset.csv", parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["year"] = df["date"].dt.year
    return df

df = load_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Filters")
    st.markdown("---")
    verticals = ["All"] + sorted(df["vertical"].unique().tolist())
    selected_vertical = st.selectbox("Vertical", verticals)
    years = ["All"] + sorted(df["year"].unique().tolist())
    selected_year = st.selectbox("Year", years)
    st.markdown("---")
    st.markdown("**Dashboard Sections**")
    show_volume   = st.checkbox("Volume & Scale",         value=True)
    show_revenue  = st.checkbox("Revenue & Margin",       value=True)
    show_risk     = st.checkbox("Risk & Failures",        value=True)
    show_perf     = st.checkbox("Performance",            value=True)
    show_sub      = st.checkbox("Subscription & Retention", value=True)
    st.markdown("---")
    st.caption("📊 Data: Synthetic · 2023–2024")

# ── Apply filters ─────────────────────────────────────────────────────────────
filtered = df.copy()
if selected_vertical != "All":
    filtered = filtered[filtered["vertical"] == selected_vertical]
if selected_year != "All":
    filtered = filtered[filtered["year"] == int(selected_year)]

# ── Chart theme ───────────────────────────────────────────────────────────────
CHART_BG   = "#161b27"
PAPER_BG   = "#161b27"
FONT_COLOR = "#c8d8f0"
GRID_COLOR = "#2a3050"
PALETTE    = ["#4a6fa5", "#4caf87", "#e09a3a", "#e05c6a", "#9b6dd1", "#3ab8c8"]

def chart_layout(fig, title="", height=320):
    fig.update_layout(
        title=dict(text=title, font=dict(family="DM Serif Display", size=14, color=FONT_COLOR)),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family="DM Sans", color=FONT_COLOR, size=11),
        height=height,
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
        xaxis=dict(gridcolor=GRID_COLOR, zeroline=False),
        yaxis=dict(gridcolor=GRID_COLOR, zeroline=False),
    )
    return fig

# ── Helper: monthly aggregation ───────────────────────────────────────────────
def monthly(col, agg="sum"):
    return filtered.groupby("month")[col].agg(agg).reset_index()

def monthly_by_vertical(col, agg="sum"):
    return filtered.groupby(["month", "vertical"])[col].agg(agg).reset_index()

# ── Header ────────────────────────────────────────────────────────────────────
col_t, col_s = st.columns([3, 1])
with col_t:
    st.markdown('<div class="dash-title">💳 Payments Analytics Dashboard</div>', unsafe_allow_html=True)
    label = selected_vertical if selected_vertical != "All" else "All Verticals"
    yr    = str(selected_year) if selected_year != "All" else "2023–2024"
    st.markdown(f'<div class="dash-subtitle">{label} · {yr}</div>', unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — VOLUME & SCALE
# ══════════════════════════════════════════════════════════════════════════════
if show_volume:
    st.markdown('<div class="section-header">📦 Volume & Scale</div>', unsafe_allow_html=True)

    total_tpv   = filtered["total_processing_volume"].sum()
    total_txns  = filtered["transaction_count"].sum()
    avg_atv     = filtered["avg_transaction_value"].mean()
    n_verticals = filtered["vertical"].nunique()

    c1, c2, c3, c4 = st.columns(4)
    for col, label, value, fmt in [
        (c1, "Total Processing Volume", total_tpv,  f"${total_tpv/1e6:.1f}M"),
        (c2, "Total Transactions",      total_txns, f"{total_txns:,.0f}"),
        (c3, "Avg Transaction Value",   avg_atv,    f"${avg_atv:.2f}"),
        (c4, "Active Verticals",        n_verticals,str(n_verticals)),
    ]:
        col.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{fmt}</div>
        </div>""", unsafe_allow_html=True)

    c_left, c_right = st.columns(2)
    with c_left:
        m = monthly("total_processing_volume")
        fig = px.area(m, x="month", y="total_processing_volume",
                      color_discrete_sequence=[PALETTE[0]])
        fig.update_traces(fill="tozeroy", line_width=2)
        chart_layout(fig, "Monthly Total Processing Volume")
        st.plotly_chart(fig, use_container_width=True)

    with c_right:
        mv = monthly_by_vertical("total_processing_volume")
        fig = px.bar(mv, x="month", y="total_processing_volume", color="vertical",
                     color_discrete_sequence=PALETTE, barmode="stack")
        chart_layout(fig, "TPV by Vertical")
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — REVENUE & MARGIN
# ══════════════════════════════════════════════════════════════════════════════
if show_revenue:
    st.markdown('<div class="section-header">💰 Revenue & Margin</div>', unsafe_allow_html=True)

    total_rev  = filtered["payment_revenue"].sum()
    total_net  = filtered["net_revenue"].sum()
    avg_margin = filtered["margin"].mean()
    avg_take   = filtered["take_rate"].mean()
    avg_cost   = filtered["cost_per_transaction"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, fmt in [
        (c1, "Payment Revenue",      f"${total_rev/1e6:.2f}M"),
        (c2, "Net Revenue",          f"${total_net/1e6:.2f}M"),
        (c3, "Avg Margin",           f"{avg_margin*100:.1f}%"),
        (c4, "Avg Take Rate",        f"{avg_take*100:.2f}%"),
        (c5, "Avg Cost / Txn",       f"${avg_cost:.2f}"),
    ]:
        col.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{fmt}</div>
        </div>""", unsafe_allow_html=True)

    c_left, c_right = st.columns(2)
    with c_left:
        m = monthly("payment_revenue")
        mn = monthly("net_revenue")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=m["month"], y=m["payment_revenue"],
                                 name="Gross Revenue", line=dict(color=PALETTE[0], width=2), fill="tozeroy"))
        fig.add_trace(go.Scatter(x=mn["month"], y=mn["net_revenue"],
                                 name="Net Revenue", line=dict(color=PALETTE[1], width=2)))
        chart_layout(fig, "Revenue vs Net Revenue")
        st.plotly_chart(fig, use_container_width=True)

    with c_right:
        vm = filtered.groupby("vertical")["margin"].mean().reset_index()
        fig = px.bar(vm, x="vertical", y="margin", color="vertical",
                     color_discrete_sequence=PALETTE)
        fig.update_layout(showlegend=False)
        fig.update_yaxes(tickformat=".1%")
        chart_layout(fig, "Avg Margin by Vertical")
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — RISK & FAILURES
# ══════════════════════════════════════════════════════════════════════════════
if show_risk:
    st.markdown('<div class="section-header">⚠️ Risk & Failures</div>', unsafe_allow_html=True)

    avg_auth       = filtered["authorization_rate"].mean()
    avg_decline    = filtered["decline_rate"].mean()
    avg_fraud      = filtered["fraud_rate"].mean()
    avg_chargeback = filtered["chargeback_rate"].mean()
    avg_refund     = filtered["refund_rate"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, fmt, good in [
        (c1, "Auth Rate",       f"{avg_auth*100:.2f}%",       True),
        (c2, "Decline Rate",    f"{avg_decline*100:.2f}%",    False),
        (c3, "Fraud Rate",      f"{avg_fraud*100:.3f}%",      False),
        (c4, "Chargeback Rate", f"{avg_chargeback*100:.3f}%", False),
        (c5, "Refund Rate",     f"{avg_refund*100:.2f}%",     False),
    ]:
        delta_cls = "kpi-delta-pos" if good else "kpi-delta-neg"
        tag = "✓ Healthy" if good else "⚠ Monitor"
        col.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{fmt}</div>
          <div class="{delta_cls}">{tag}</div>
        </div>""", unsafe_allow_html=True)

    c_left, c_right = st.columns(2)
    with c_left:
        m_fraud = monthly("fraud_rate", "mean")
        m_cb    = monthly("chargeback_rate", "mean")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=m_fraud["month"], y=m_fraud["fraud_rate"]*100,
                                 name="Fraud Rate %", line=dict(color=PALETTE[3], width=2)))
        fig.add_trace(go.Scatter(x=m_cb["month"], y=m_cb["chargeback_rate"]*100,
                                 name="Chargeback Rate %", line=dict(color=PALETTE[2], width=2, dash="dash")))
        chart_layout(fig, "Fraud & Chargeback Rates Over Time")
        st.plotly_chart(fig, use_container_width=True)

    with c_right:
        vd = filtered.groupby("vertical")["decline_rate"].mean().reset_index()
        fig = px.bar(vd, x="vertical", y="decline_rate", color="vertical",
                     color_discrete_sequence=PALETTE)
        fig.update_yaxes(tickformat=".2%")
        fig.update_layout(showlegend=False)
        chart_layout(fig, "Avg Decline Rate by Vertical")
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — PERFORMANCE & RELIABILITY
# ══════════════════════════════════════════════════════════════════════════════
if show_perf:
    st.markdown('<div class="section-header">⚙️ Performance & Reliability</div>', unsafe_allow_html=True)

    avg_success  = filtered["payment_success_rate"].mean()
    avg_latency  = filtered["latency_ms"].mean()
    avg_uptime   = filtered["uptime"].mean()
    avg_recovery = filtered["failed_payment_recovery_rate"].mean()

    c1, c2, c3, c4 = st.columns(4)
    for col, label, fmt in [
        (c1, "Payment Success Rate",      f"{avg_success*100:.2f}%"),
        (c2, "Avg Latency (ms)",          f"{avg_latency:.0f} ms"),
        (c3, "System Uptime",             f"{avg_uptime*100:.3f}%"),
        (c4, "Failed Payment Recovery",   f"{avg_recovery*100:.1f}%"),
    ]:
        col.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{fmt}</div>
        </div>""", unsafe_allow_html=True)

    c_left, c_right = st.columns(2)
    with c_left:
        m = monthly("latency_ms", "mean")
        fig = px.line(m, x="month", y="latency_ms", color_discrete_sequence=[PALETTE[4]])
        fig.update_traces(line_width=2)
        fig.add_hline(y=500, line_dash="dash", line_color=PALETTE[3],
                      annotation_text="500ms threshold")
        chart_layout(fig, "Avg Transaction Latency (ms)")
        st.plotly_chart(fig, use_container_width=True)

    with c_right:
        m = monthly("payment_success_rate", "mean")
        fig = px.area(m, x="month", y="payment_success_rate",
                      color_discrete_sequence=[PALETTE[1]])
        fig.update_traces(fill="tozeroy", line_width=2)
        fig.update_yaxes(tickformat=".2%", range=[0.9, 1.0])
        chart_layout(fig, "Monthly Payment Success Rate")
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — SUBSCRIPTION & RETENTION
# ══════════════════════════════════════════════════════════════════════════════
if show_sub:
    st.markdown('<div class="section-header">🔄 Subscription & Retention</div>', unsafe_allow_html=True)

    avg_t2p      = filtered["trial_to_paid_rate"].mean()
    avg_inv_churn= filtered["involuntary_churn_rate"].mean()
    avg_dunning  = filtered["dunning_recovery_rate"].mean()
    total_mrr    = filtered.groupby("month")["mrr"].sum().mean()
    avg_nrr      = filtered["net_revenue_retention"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, fmt in [
        (c1, "Trial → Paid Rate",     f"{avg_t2p*100:.1f}%"),
        (c2, "Involuntary Churn",     f"{avg_inv_churn*100:.2f}%"),
        (c3, "Dunning Recovery",      f"{avg_dunning*100:.1f}%"),
        (c4, "Avg Monthly MRR",       f"${total_mrr/1e3:.1f}K"),
        (c5, "Net Revenue Retention", f"{avg_nrr*100:.1f}%"),
    ]:
        col.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{fmt}</div>
        </div>""", unsafe_allow_html=True)

    c_left, c_right = st.columns(2)
    with c_left:
        mrr_m = filtered.groupby("month")["mrr"].sum().reset_index()
        fig = px.bar(mrr_m, x="month", y="mrr", color_discrete_sequence=[PALETTE[0]])
        chart_layout(fig, "Monthly Recurring Revenue (MRR)")
        st.plotly_chart(fig, use_container_width=True)

    with c_right:
        sub_v = filtered.groupby("vertical").agg(
            trial_to_paid=("trial_to_paid_rate","mean"),
            dunning=("dunning_recovery_rate","mean"),
            inv_churn=("involuntary_churn_rate","mean")
        ).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Trial→Paid", x=sub_v["vertical"],
                             y=sub_v["trial_to_paid"]*100, marker_color=PALETTE[1]))
        fig.add_trace(go.Bar(name="Dunning Recovery", x=sub_v["vertical"],
                             y=sub_v["dunning"]*100, marker_color=PALETTE[0]))
        fig.add_trace(go.Bar(name="Involuntary Churn", x=sub_v["vertical"],
                             y=sub_v["inv_churn"]*100, marker_color=PALETTE[3]))
        fig.update_layout(barmode="group")
        chart_layout(fig, "Subscription KPIs by Vertical")
        st.plotly_chart(fig, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center;color:#3a4a60;font-size:0.75rem;">'
    'Payments Analytics Dashboard · Built with Streamlit & Plotly · Synthetic Data 2023–2024'
    '</p>', unsafe_allow_html=True
)
