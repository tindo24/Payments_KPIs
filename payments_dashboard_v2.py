import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ───────────────────────────────────────────────────────────────
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

  section[data-testid="stSidebar"] {
    background: #161b27;
    border-right: 1px solid #2a2f3d;
  }
  section[data-testid="stSidebar"] * { color: #c8cdd8 !important; }

  .kpi-card {
    background: linear-gradient(135deg, #1a2035 0%, #1e2640 100%);
    border: 1px solid #2a3050;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.5rem;
    transition: border-color 0.2s;
  }
  .kpi-card:hover { border-color: #24900e; }
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
  .kpi-delta-pos { font-size: 0.78rem; color: #00d084; font-weight: 500; }
  .kpi-delta-neg { font-size: 0.78rem; color: #ff6900; font-weight: 500; }

  .section-header {
    font-family: 'DM Serif Display', serif;
    font-size: 1.15rem;
    color: #c8d8f0;
    border-left: 3px solid #24900e;
    padding-left: 0.75rem;
    margin: 1.2rem 0 0.6rem 0;
  }

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

  .tab-intro {
    background: linear-gradient(135deg, #1a2035 0%, #1e2640 100%);
    border: 1px solid #2a3050;
    border-radius: 10px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 1rem;
    font-size: 0.85rem;
    color: #8a9ab0;
    line-height: 1.6;
  }

  /* KPI Definition table */
  .def-card {
    background: #161b27;
    border: 1px solid #2a3050;
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.5rem;
  }
  .def-kpi-name {
    font-weight: 600;
    color: #c8d8f0;
    font-size: 0.9rem;
  }
  .def-kpi-def {
    color: #7a8aa0;
    font-size: 0.82rem;
    margin-top: 0.2rem;
    line-height: 1.5;
  }
  .def-kpi-target {
    color: #00d084;
    font-size: 0.78rem;
    margin-top: 0.2rem;
    font-weight: 500;
  }
  .def-category-badge {
    display: inline-block;
    background: #1a3a1a;
    color: #00d084;
    border-radius: 4px;
    padding: 0.1rem 0.5rem;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
  }

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
    font-size: 0.85rem;
    font-weight: 500;
    letter-spacing: 0.03em;
    padding: 0.5rem 1.2rem;
  }
  .stTabs [aria-selected="true"] {
    background: #1a3a1a !important;
    color: #00d084 !important;
  }
</style>
""", unsafe_allow_html=True)

# ── KPI Definitions data ──────────────────────────────────────────────────────
KPI_DEFS = [
    ("Volume & Scale",           "Total Processing Volume (TPV)",  "The total dollar value of all payment transactions processed within a given period. The primary measure of payment ecosystem scale.", ""),
    ("Volume & Scale",           "Transaction Count",              "The total number of individual payment transactions processed. Used alongside TPV to understand average transaction size and volume trends.", ""),
    ("Volume & Scale",           "Average Transaction Value (ATV)","Total Processing Volume divided by Transaction Count. Indicates the typical size of a single payment and helps identify shifts in customer behavior or pricing.", ""),
    ("Revenue & Margin",         "Payment Revenue",                "Gross revenue earned from payment processing fees charged to customers. Calculated as TPV multiplied by the Take Rate.", ""),
    ("Revenue & Margin",         "Net Revenue",                    "Payment Revenue minus total processing costs. Represents the true profitability of the payment operation after direct costs.", ""),
    ("Revenue & Margin",         "Margin %",                       "Net Revenue divided by Payment Revenue. Measures how efficiently the payment ecosystem converts gross revenue into profit.", ""),
    ("Revenue & Margin",         "Take Rate",                      "The percentage of TPV retained as payment revenue. A core pricing economics metric that reflects the value captured per dollar processed.", ""),
    ("Revenue & Margin",         "Cost per Transaction",           "Total processing costs divided by Transaction Count. Used to benchmark operational efficiency and identify cost optimization opportunities.", ""),
    ("Revenue & Margin",         "Processing Cost",                "The total direct cost of processing payments including interchange fees, network fees, and payment processor charges.", ""),
    ("Risk & Failures",          "Authorization Rate",             "The percentage of payment attempts successfully approved by the issuing bank or payment network. A high authorization rate indicates a healthy payment flow.", "Target: above 95%"),
    ("Risk & Failures",          "Decline Rate",                   "The percentage of payment attempts that are rejected. High decline rates directly impact revenue and customer experience.", ""),
    ("Risk & Failures",          "Fraud Rate",                     "The percentage of transactions identified as fraudulent. Monitored closely to protect customers and manage chargeback exposure.", "Target: below 0.5%"),
    ("Risk & Failures",          "Chargeback Rate",                "The percentage of transactions disputed by customers and reversed by their bank. Elevated chargeback rates can trigger card network penalties.", "Target: below 1%"),
    ("Risk & Failures",          "Refund Rate",                    "The percentage of transactions voluntarily reversed by the merchant. High refund rates may signal product, billing, or satisfaction issues.", ""),
    ("Performance & Reliability","Payment Success Rate",           "The percentage of initiated payment transactions completed successfully end to end. Combines authorization, processing, and settlement outcomes.", ""),
    ("Performance & Reliability","Transaction Latency (ms)",       "The average time in milliseconds to process a single payment transaction. Latency above 500ms may indicate pipeline or infrastructure issues.", "Target: below 500ms"),
    ("Performance & Reliability","System Uptime",                  "The percentage of time the payment processing system is fully operational.", "Target: 99.9% or above"),
    ("Performance & Reliability","Failed Payment Recovery Rate",   "The percentage of initially failed payments successfully recovered through retry logic or dunning workflows.", ""),
    ("Subscription & Retention", "Trial-to-Paid Conversion Rate",  "The percentage of trial users who convert to a paid subscription within a defined window. A primary indicator of product-market fit and pricing effectiveness.", ""),
    ("Subscription & Retention", "Involuntary Churn Rate",         "The percentage of subscribers lost due to payment failures rather than active cancellations. Directly addressable through dunning and retry strategies.", ""),
    ("Subscription & Retention", "Dunning Recovery Rate",          "The percentage of failed subscription payments successfully recovered through automated retry and customer outreach workflows.", ""),
    ("Subscription & Retention", "Monthly Recurring Revenue (MRR)","The predictable, normalized monthly revenue generated from active subscriptions. The primary health metric for subscription-based payment models.", ""),
    ("Subscription & Retention", "Net Revenue Retention (NRR)",    "Revenue retained from existing customers after accounting for churn, contractions, and expansions. NRR above 100% indicates growth from existing customers alone.", "Target: above 100%"),
]
kpi_df = pd.DataFrame(KPI_DEFS, columns=["Category", "KPI Name", "Definition", "Target"])

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("payments_dataset.csv", parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["year"]  = df["date"].dt.year
    return df

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Filters")
    st.markdown("---")
    verticals      = ["All"] + sorted(df["vertical"].unique().tolist())
    selected_vert  = st.selectbox("Vertical", verticals)
    years          = ["All"] + sorted(df["year"].unique().tolist())
    selected_year  = st.selectbox("Year", years)
    st.markdown("---")
    st.caption("📊 Synthetic Data · 2023–2024")
    st.caption("👥 Tabs: Finance · Product · Operations · KPI Definitions")

# ── Filter ────────────────────────────────────────────────────────────────────
filtered = df.copy()
if selected_vert != "All":
    filtered = filtered[filtered["vertical"] == selected_vert]
if selected_year != "All":
    filtered = filtered[filtered["year"] == int(selected_year)]

# ── Chart helpers ─────────────────────────────────────────────────────────────
CHART_BG   = "#161b27"
PAPER_BG   = "#161b27"
FONT_COLOR = "#c8d8f0"
GRID_COLOR = "#2a3050"
PALETTE    = ["#24900e","#0693e3","#ff6900","#9b51e0","#00d084","#7bdcb5"]

def clayout(fig, title="", height=300):
    fig.update_layout(
        title=dict(text=title, font=dict(family="DM Serif Display", size=13, color=FONT_COLOR)),
        paper_bgcolor=PAPER_BG, plot_bgcolor=CHART_BG,
        font=dict(family="DM Sans", color=FONT_COLOR, size=11),
        height=height, margin=dict(l=10, r=10, t=38, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
        xaxis=dict(gridcolor=GRID_COLOR, zeroline=False),
        yaxis=dict(gridcolor=GRID_COLOR, zeroline=False),
    )
    return fig

def kpi_card(col, label, value, tag=None, good=True):
    delta_cls = "kpi-delta-pos" if good else "kpi-delta-neg"
    tag_html  = f'<div class="{delta_cls}">{tag}</div>' if tag else ""
    col.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      {tag_html}
    </div>""", unsafe_allow_html=True)

def monthly(col, agg="sum"):
    return filtered.groupby("month")[col].agg(agg).reset_index()

def by_vertical(col, agg="mean"):
    return filtered.groupby("vertical")[col].agg(agg).reset_index()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="dash-title">💳 Payments Analytics Dashboard</div>', unsafe_allow_html=True)
label = selected_vert if selected_vert != "All" else "All Verticals"
yr    = str(selected_year) if selected_year != "All" else "2023–2024"
st.markdown(f'<div class="dash-subtitle">{label} · {yr}</div>', unsafe_allow_html=True)
st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_finance, tab_product, tab_ops, tab_defs = st.tabs([
    "💰  Finance", "📱  Product", "⚙️  Operations", "📖  KPI Definitions"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — FINANCE
# ══════════════════════════════════════════════════════════════════════════════
with tab_finance:
    st.markdown('<div class="tab-intro">📊 <strong>Finance View</strong> — Focused on processing volumes, revenue performance, margin analysis, pricing economics, and cost drivers. Designed for recurring executive reporting and financial reconciliation.</div>', unsafe_allow_html=True)

    # ── Volume & Scale KPIs
    st.markdown('<div class="section-header">📦 Volume & Scale</div>', unsafe_allow_html=True)
    total_tpv  = filtered["total_processing_volume"].sum()
    total_txns = filtered["transaction_count"].sum()
    avg_atv    = filtered["avg_transaction_value"].mean()

    c1, c2, c3 = st.columns(3)
    kpi_card(c1, "Total Processing Volume", f"${total_tpv/1e6:.1f}M")
    kpi_card(c2, "Total Transactions",      f"{total_txns:,.0f}")
    kpi_card(c3, "Avg Transaction Value",   f"${avg_atv:.2f}")

    c_left, c_right = st.columns(2)
    with c_left:
        m = monthly("total_processing_volume")
        fig = px.area(m, x="month", y="total_processing_volume", color_discrete_sequence=[PALETTE[0]])
        fig.update_traces(fill="tozeroy", line_width=2)
        clayout(fig, "Monthly Total Processing Volume")
        st.plotly_chart(fig, use_container_width=True)
    with c_right:
        mv = filtered.groupby(["month","vertical"])["total_processing_volume"].sum().reset_index()
        fig = px.bar(mv, x="month", y="total_processing_volume", color="vertical",
                     color_discrete_sequence=PALETTE, barmode="stack")
        clayout(fig, "TPV by Vertical")
        st.plotly_chart(fig, use_container_width=True)

    # ── Revenue & Margin KPIs
    st.markdown('<div class="section-header">💰 Revenue & Margin</div>', unsafe_allow_html=True)
    total_rev  = filtered["payment_revenue"].sum()
    total_net  = filtered["net_revenue"].sum()
    avg_margin = filtered["margin"].mean()
    avg_take   = filtered["take_rate"].mean()
    avg_cost   = filtered["cost_per_transaction"].mean()
    total_cost = filtered["processing_cost"].sum()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    kpi_card(c1, "Payment Revenue",    f"${total_rev/1e6:.2f}M")
    kpi_card(c2, "Net Revenue",        f"${total_net/1e6:.2f}M")
    kpi_card(c3, "Avg Margin",         f"{avg_margin*100:.1f}%")
    kpi_card(c4, "Avg Take Rate",      f"{avg_take*100:.2f}%")
    kpi_card(c5, "Cost / Transaction", f"${avg_cost:.2f}")
    kpi_card(c6, "Total Processing Cost", f"${total_cost/1e6:.2f}M")

    c_left, c_right = st.columns(2)
    with c_left:
        m  = monthly("payment_revenue")
        mn = monthly("net_revenue")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=m["month"], y=m["payment_revenue"],
                                 name="Gross Revenue", line=dict(color=PALETTE[0], width=2), fill="tozeroy"))
        fig.add_trace(go.Scatter(x=mn["month"], y=mn["net_revenue"],
                                 name="Net Revenue", line=dict(color=PALETTE[1], width=2)))
        clayout(fig, "Revenue vs Net Revenue")
        st.plotly_chart(fig, use_container_width=True)
    with c_right:
        vm = by_vertical("margin")
        fig = px.bar(vm, x="vertical", y="margin", color="vertical",
                     color_discrete_sequence=PALETTE)
        fig.update_yaxes(tickformat=".1%")
        fig.update_layout(showlegend=False)
        clayout(fig, "Avg Margin by Vertical")
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PRODUCT
# ══════════════════════════════════════════════════════════════════════════════
with tab_product:
    st.markdown('<div class="tab-intro">📱 <strong>Product View</strong> — Focused on subscription health, customer penetration, pricing economics, trial conversion, and retention. Designed to inform product decisions and new payment initiative readiness.</div>', unsafe_allow_html=True)

    # ── Subscription KPIs
    st.markdown('<div class="section-header">🔄 Subscription & Retention</div>', unsafe_allow_html=True)
    avg_t2p       = filtered["trial_to_paid_rate"].mean()
    avg_inv_churn = filtered["involuntary_churn_rate"].mean()
    avg_dunning   = filtered["dunning_recovery_rate"].mean()
    total_mrr     = filtered.groupby("month")["mrr"].sum().mean()
    avg_nrr       = filtered["net_revenue_retention"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    kpi_card(c1, "Trial → Paid Rate",     f"{avg_t2p*100:.1f}%",        tag="↑ Growth lever",  good=True)
    kpi_card(c2, "Involuntary Churn",     f"{avg_inv_churn*100:.2f}%",  tag="⚠ Monitor",       good=False)
    kpi_card(c3, "Dunning Recovery",      f"{avg_dunning*100:.1f}%",    tag="↑ Revenue save",  good=True)
    kpi_card(c4, "Avg Monthly MRR",       f"${total_mrr/1e3:.1f}K")
    kpi_card(c5, "Net Revenue Retention", f"{avg_nrr*100:.1f}%",        tag="✓ Healthy" if avg_nrr >= 1 else "⚠ Below 100%", good=avg_nrr >= 1)

    c_left, c_right = st.columns(2)
    with c_left:
        mrr_m = filtered.groupby("month")["mrr"].sum().reset_index()
        fig = px.bar(mrr_m, x="month", y="mrr", color_discrete_sequence=[PALETTE[0]])
        clayout(fig, "Monthly Recurring Revenue (MRR)")
        st.plotly_chart(fig, use_container_width=True)
    with c_right:
        sub_v = filtered.groupby("vertical").agg(
            trial_to_paid=("trial_to_paid_rate","mean"),
            dunning=("dunning_recovery_rate","mean"),
            inv_churn=("involuntary_churn_rate","mean")
        ).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Trial→Paid %",      x=sub_v["vertical"], y=sub_v["trial_to_paid"]*100, marker_color=PALETTE[1]))
        fig.add_trace(go.Bar(name="Dunning Recovery %", x=sub_v["vertical"], y=sub_v["dunning"]*100,       marker_color=PALETTE[0]))
        fig.add_trace(go.Bar(name="Involuntary Churn %",x=sub_v["vertical"], y=sub_v["inv_churn"]*100,     marker_color=PALETTE[3]))
        fig.update_layout(barmode="group")
        clayout(fig, "Subscription KPIs by Vertical")
        st.plotly_chart(fig, use_container_width=True)

    # ── NRR Trend
    st.markdown('<div class="section-header">📈 NRR Trend</div>', unsafe_allow_html=True)
    nrr_m = monthly("net_revenue_retention", "mean")
    fig = px.line(nrr_m, x="month", y="net_revenue_retention", color_discrete_sequence=[PALETTE[4]])
    fig.update_traces(line_width=2)
    fig.add_hline(y=1.0, line_dash="dash", line_color=PALETTE[1], annotation_text="100% target")
    fig.update_yaxes(tickformat=".1%")
    clayout(fig, "Net Revenue Retention Over Time", height=260)
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab_ops:
    st.markdown('<div class="tab-intro">⚙️ <strong>Operations View</strong> — Focused on payment performance, risk monitoring, system reliability, and failure root cause analysis. Designed to surface anomalies and optimization opportunities across the payment ecosystem.</div>', unsafe_allow_html=True)

    # ── Risk KPIs
    st.markdown('<div class="section-header">⚠️ Risk & Failures</div>', unsafe_allow_html=True)
    avg_auth  = filtered["authorization_rate"].mean()
    avg_dec   = filtered["decline_rate"].mean()
    avg_fraud = filtered["fraud_rate"].mean()
    avg_cb    = filtered["chargeback_rate"].mean()
    avg_ref   = filtered["refund_rate"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    kpi_card(c1, "Authorization Rate", f"{avg_auth*100:.2f}%",  tag="✓ Healthy",  good=True)
    kpi_card(c2, "Decline Rate",       f"{avg_dec*100:.2f}%",   tag="⚠ Monitor",  good=False)
    kpi_card(c3, "Fraud Rate",         f"{avg_fraud*100:.3f}%", tag="⚠ Monitor",  good=False)
    kpi_card(c4, "Chargeback Rate",    f"{avg_cb*100:.3f}%",    tag="⚠ Monitor",  good=False)
    kpi_card(c5, "Refund Rate",        f"{avg_ref*100:.2f}%",   tag="⚠ Monitor",  good=False)

    c_left, c_right = st.columns(2)
    with c_left:
        mf = monthly("fraud_rate","mean")
        mc = monthly("chargeback_rate","mean")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=mf["month"], y=mf["fraud_rate"]*100,
                                 name="Fraud Rate %", line=dict(color=PALETTE[3], width=2)))
        fig.add_trace(go.Scatter(x=mc["month"], y=mc["chargeback_rate"]*100,
                                 name="Chargeback Rate %", line=dict(color=PALETTE[2], width=2, dash="dash")))
        clayout(fig, "Fraud & Chargeback Rates Over Time")
        st.plotly_chart(fig, use_container_width=True)
    with c_right:
        vd = by_vertical("decline_rate")
        fig = px.bar(vd, x="vertical", y="decline_rate", color="vertical",
                     color_discrete_sequence=PALETTE)
        fig.update_yaxes(tickformat=".2%")
        fig.update_layout(showlegend=False)
        clayout(fig, "Avg Decline Rate by Vertical")
        st.plotly_chart(fig, use_container_width=True)

    # ── Performance KPIs
    st.markdown('<div class="section-header">⚙️ Performance & Reliability</div>', unsafe_allow_html=True)
    avg_success  = filtered["payment_success_rate"].mean()
    avg_latency  = filtered["latency_ms"].mean()
    avg_uptime   = filtered["uptime"].mean()
    avg_recovery = filtered["failed_payment_recovery_rate"].mean()

    c1, c2, c3, c4 = st.columns(4)
    kpi_card(c1, "Payment Success Rate",    f"{avg_success*100:.2f}%",  tag="✓ Healthy", good=True)
    kpi_card(c2, "Avg Latency (ms)",        f"{avg_latency:.0f} ms",    tag="✓ Normal" if avg_latency < 500 else "⚠ High", good=avg_latency < 500)
    kpi_card(c3, "System Uptime",           f"{avg_uptime*100:.3f}%",   tag="✓ Healthy", good=True)
    kpi_card(c4, "Failed Payment Recovery", f"{avg_recovery*100:.1f}%")

    c_left, c_right = st.columns(2)
    with c_left:
        ml = monthly("latency_ms","mean")
        fig = px.line(ml, x="month", y="latency_ms", color_discrete_sequence=[PALETTE[4]])
        fig.update_traces(line_width=2)
        fig.add_hline(y=500, line_dash="dash", line_color=PALETTE[3], annotation_text="500ms threshold")
        clayout(fig, "Avg Transaction Latency (ms)")
        st.plotly_chart(fig, use_container_width=True)
    with c_right:
        ms = monthly("payment_success_rate","mean")
        fig = px.area(ms, x="month", y="payment_success_rate", color_discrete_sequence=[PALETTE[1]])
        fig.update_traces(fill="tozeroy", line_width=2)
        fig.update_yaxes(tickformat=".2%", range=[0.9, 1.0])
        clayout(fig, "Monthly Payment Success Rate")
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — KPI DEFINITIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab_defs:
    st.markdown('<div class="tab-intro">📖 <strong>KPI Definitions</strong> — Standardized definitions for all payment metrics used across Finance, Product, and Operations views. Filter by category to find specific metrics quickly.</div>', unsafe_allow_html=True)

    categories = ["All"] + sorted(kpi_df["Category"].unique().tolist())
    search_cat = st.selectbox("Filter by Category", categories)
    search_term = st.text_input("Search by KPI name or keyword", placeholder="e.g. chargeback, margin, MRR...")

    display_df = kpi_df.copy()
    if search_cat != "All":
        display_df = display_df[display_df["Category"] == search_cat]
    if search_term:
        mask = (
            display_df["KPI Name"].str.contains(search_term, case=False) |
            display_df["Definition"].str.contains(search_term, case=False)
        )
        display_df = display_df[mask]

    st.markdown(f"**Showing {len(display_df)} of {len(kpi_df)} KPIs**")
    st.markdown("")

    for _, row in display_df.iterrows():
        target_html = f'<div class="def-kpi-target">🎯 {row["Target"]}</div>' if row["Target"] else ""
        st.markdown(f"""
        <div class="def-card">
          <div class="def-category-badge">{row['Category']}</div>
          <div class="def-kpi-name">{row['KPI Name']}</div>
          <div class="def-kpi-def">{row['Definition']}</div>
          {target_html}
        </div>""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center;color:#3a4a60;font-size:0.75rem;">'
    'Payments Analytics Dashboard · Finance · Product · Operations · '
    'Built with Streamlit & Plotly · Synthetic Data 2023–2024'
    '</p>', unsafe_allow_html=True
)
