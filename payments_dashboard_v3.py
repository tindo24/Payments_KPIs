import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Payments Analytics | Togetherwork",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: #0f1117; color: #e8e8e8; }
  .main { background-color: #0f1117; }
  .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
  section[data-testid="stSidebar"] { background: #161b27; border-right: 1px solid #2a2f3d; }
  section[data-testid="stSidebar"] * { color: #c8cdd8 !important; }
  .kpi-card {
    background: linear-gradient(135deg, #1a2035 0%, #1e2640 100%);
    border: 1px solid #2a3050; border-radius: 12px;
    padding: 1.2rem 1.4rem; margin-bottom: 0.5rem; transition: border-color 0.2s;
  }
  .kpi-card:hover { border-color: #4a6fa5; }
  .kpi-label { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #7a8aa0; margin-bottom: 0.3rem; }
  .kpi-value { font-family: 'DM Serif Display', serif; font-size: 1.9rem; color: #e8eaf6; line-height: 1.1; }
  .kpi-delta-pos { font-size: 0.78rem; color: #4caf87; font-weight: 500; }
  .kpi-delta-neg { font-size: 0.78rem; color: #e05c6a; font-weight: 500; }
  .section-header { font-family: 'DM Serif Display', serif; font-size: 1.15rem; color: #c8d8f0; border-left: 3px solid #4a6fa5; padding-left: 0.75rem; margin: 1.2rem 0 0.6rem 0; }
  .dash-title { font-family: 'DM Serif Display', serif; font-size: 2rem; color: #c8d8f0; margin-bottom: 0; }
  .dash-subtitle { font-size: 0.85rem; color: #5a6a80; margin-top: 0.1rem; }
  .tab-intro { background: linear-gradient(135deg, #1a2035 0%, #1e2640 100%); border: 1px solid #2a3050; border-radius: 10px; padding: 0.9rem 1.2rem; margin-bottom: 1rem; font-size: 0.85rem; color: #8a9ab0; line-height: 1.6; }
  .insight-box { background: linear-gradient(135deg, #1a2e20 0%, #1e3525 100%); border: 1px solid #2a5035; border-radius: 10px; padding: 0.9rem 1.2rem; margin-bottom: 0.8rem; }
  .insight-title { font-weight: 700; color: #4caf87; font-size: 0.85rem; margin-bottom: 0.3rem; }
  .insight-body { color: #8ab0a0; font-size: 0.8rem; line-height: 1.5; }
  .credit-card { background: linear-gradient(135deg, #1e2a45 0%, #1a2550 100%); border: 1px solid #3a5080; border-radius: 12px; padding: 1.2rem 1.4rem; margin-bottom: 0.5rem; }
  .credit-tier { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #7a9ad0; margin-bottom: 0.2rem; }
  .credit-amount { font-family: 'DM Serif Display', serif; font-size: 1.6rem; color: #c8d8f0; }
  .credit-sub { font-size: 0.75rem; color: #5a7aa0; margin-top: 0.2rem; }
  .def-card { background: #161b27; border: 1px solid #2a3050; border-radius: 10px; padding: 0.9rem 1.1rem; margin-bottom: 0.5rem; }
  .def-kpi-name { font-weight: 600; color: #c8d8f0; font-size: 0.9rem; }
  .def-kpi-def { color: #7a8aa0; font-size: 0.82rem; margin-top: 0.2rem; line-height: 1.5; }
  .def-kpi-target { color: #4caf87; font-size: 0.78rem; margin-top: 0.2rem; font-weight: 500; }
  .def-category-badge { display: inline-block; background: #2a3a5c; color: #7a9ad0; border-radius: 4px; padding: 0.1rem 0.5rem; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 0.4rem; }
  .stTabs [data-baseweb="tab-list"] { background: #161b27; border-radius: 8px; gap: 4px; padding: 4px; }
  .stTabs [data-baseweb="tab"] { background: transparent; color: #7a8aa0; border-radius: 6px; font-size: 0.82rem; font-weight: 500; letter-spacing: 0.03em; padding: 0.5rem 1rem; }
  .stTabs [aria-selected="true"] { background: #2a3a5c !important; color: #c8d8f0 !important; }
</style>
""", unsafe_allow_html=True)

# ── KPI Definitions ───────────────────────────────────────────────────────────
KPI_DEFS = [
    ("Volume & Scale","Total Processing Volume (TPV)","The total dollar value of all payment transactions processed within a given period.",""),
    ("Volume & Scale","Transaction Count","The total number of individual payment transactions processed.",""),
    ("Volume & Scale","Average Transaction Value (ATV)","Total Processing Volume divided by Transaction Count.",""),
    ("Revenue & Margin","Payment Revenue","Gross fees earned. TPV × Take Rate.",""),
    ("Revenue & Margin","Net Revenue","Payment Revenue minus processing costs.",""),
    ("Revenue & Margin","Margin %","Net Revenue / Payment Revenue.",""),
    ("Revenue & Margin","Take Rate","% of TPV retained as revenue. Togetherwork keeps 1% of every 3% charged.",""),
    ("Revenue & Margin","Cost per Transaction","Total processing cost / Transaction Count.",""),
    ("Revenue & Margin","Processing Cost","Total direct cost: interchange (1.8%) + processor (0.2%) = 2.0% of TPV.",""),
    ("Cost Breakdown","Interchange Fee (Card Networks)","1.8% of TPV paid to Visa/Mastercard. Largest cost component. Not negotiable directly.",""),
    ("Cost Breakdown","Processor Fee (Stripe)","0.2% of TPV paid to Stripe. Negotiable at volume. Key target for rate optimization.",""),
    ("Cost Breakdown","Togetherwork Net Take","1.0% of TPV retained as revenue after paying card networks and Stripe.",""),
    ("Cost Breakdown","Blended Cost Rate","Total cost as % of TPV (interchange + processor). Currently ~2.0% of every transaction.",""),
    ("Risk & Failures","Authorization Rate","% approved by issuing bank. Target above 95%.","Target: above 95%"),
    ("Risk & Failures","Decline Rate","% rejected. High rates = lost revenue.",""),
    ("Risk & Failures","Fraud Rate","% flagged fraudulent.","Target: below 0.5%"),
    ("Risk & Failures","Chargeback Rate","% disputed. Above 1.5% risks card network penalties.","Target: below 1%"),
    ("Risk & Failures","Refund Rate","% voluntarily reversed.",""),
    ("Performance","Payment Success Rate","End-to-end % completed successfully.",""),
    ("Performance","Transaction Latency (ms)","Avg ms to process. Target below 500ms.","Target: below 500ms"),
    ("Performance","System Uptime","% system operational. Target 99.9%+.","Target: 99.9%+"),
    ("Performance","Failed Payment Recovery Rate","% of failed payments recovered through retry/dunning.",""),
    ("Subscription & Retention","Trial-to-Paid Conversion","% of trials converting to paid.",""),
    ("Subscription & Retention","Involuntary Churn Rate","% lost to payment failures — not cancellations.",""),
    ("Subscription & Retention","Dunning Recovery Rate","% of failed payments recovered. World-class: 60-75%.",""),
    ("Subscription & Retention","MRR","Monthly Recurring Revenue from active subscriptions.",""),
    ("Subscription & Retention","Net Revenue Retention (NRR)","Revenue retained from existing customers. Above 100% = growth without new clients.","Target: above 100%"),
    ("Client Intelligence","Payment Engagement Score","Composite score (0-100) measuring client usage intensity based on TPV, transaction frequency, and product adoption.",""),
    ("Client Intelligence","Credit Eligibility Tier","Creditworthiness tier (Platinum/Gold/Silver/Watch) derived from payment history, volume consistency, and chargeback rate.",""),
    ("Client Intelligence","Estimated Credit Line","Estimated working capital credit line based on annualized TPV and payment health score.",""),
    ("Client Intelligence","Volume Tier (Stripe Negotiation)","Cumulative TPV tier used to benchmark Stripe rate negotiation. Higher volume = lower processor fees.",""),
]
kpi_df = pd.DataFrame(KPI_DEFS, columns=["Category","KPI Name","Definition","Target"])

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("payments_dataset.csv", parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["year"]  = df["date"].dt.year

    # ── Derive cost breakdown columns from actual fee structure ───────────────
    # Togetherwork charges 3% total:
    # 1.8% → card networks (interchange)
    # 0.2% → Stripe (processor)
    # 1.0% → Togetherwork (take rate)
    df["interchange_cost"]   = df["total_processing_volume"] * 0.018
    df["stripe_cost"]        = df["total_processing_volume"] * 0.002
    df["tw_net_revenue"]     = df["total_processing_volume"] * 0.010
    df["total_fee_collected"]= df["total_processing_volume"] * 0.030
    df["blended_cost_rate"]  = 0.020  # 1.8 + 0.2

    # ── Derive client usage / engagement metrics ──────────────────────────────
    # Payment Engagement Score: composite of normalized TPV, txn frequency, success rate
    df["txn_intensity"]      = df["transaction_count"] / df["transaction_count"].max()
    df["tpv_intensity"]      = df["total_processing_volume"] / df["total_processing_volume"].max()
    df["engagement_score"]   = (
        df["txn_intensity"]       * 35 +
        df["tpv_intensity"]       * 35 +
        df["payment_success_rate"]* 20 +
        (1 - df["chargeback_rate"] * 50) * 10
    ).clip(0, 100).round(1)

    # ── Annualized TPV per vertical (for credit line estimation) ──────────────
    return df

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Filters")
    st.markdown("---")
    verticals     = ["All"] + sorted(df["vertical"].unique().tolist())
    selected_vert = st.selectbox("Vertical", verticals)
    years         = ["All"] + sorted(df["year"].unique().tolist())
    selected_year = st.selectbox("Year", years)
    st.markdown("---")
    st.caption("📊 Synthetic Data · 2023–2024")
    st.caption("Fee Structure: 3% total · 1.8% interchange · 0.2% Stripe · 1.0% TW")

# ── Filter ────────────────────────────────────────────────────────────────────
filtered = df.copy()
if selected_vert != "All":
    filtered = filtered[filtered["vertical"] == selected_vert]
if selected_year != "All":
    filtered = filtered[filtered["year"] == int(selected_year)]

# ── Chart helpers ─────────────────────────────────────────────────────────────
CHART_BG = PAPER_BG = "#161b27"
FONT_COLOR = "#c8d8f0"
GRID_COLOR = "#2a3050"
PALETTE = ["#4a6fa5","#4caf87","#e09a3a","#e05c6a","#9b6dd1","#3ab8c8"]

def clayout(fig, title="", height=300):
    fig.update_layout(
        title=dict(text=title, font=dict(family="DM Serif Display", size=13, color=FONT_COLOR)),
        paper_bgcolor=PAPER_BG, plot_bgcolor=CHART_BG,
        font=dict(family="DM Sans", color=FONT_COLOR, size=11),
        height=height, margin=dict(l=10,r=10,t=38,b=10),
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
st.markdown(f'<div class="dash-subtitle">{label} · {yr} · Fee Structure: 3.0% total charged → 1.8% interchange · 0.2% Stripe · 1.0% Togetherwork</div>', unsafe_allow_html=True)
st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_finance, tab_product, tab_ops, tab_defs = st.tabs([
    "💰  Finance", "📱  Product & Client Intelligence", "⚙️  Operations", "📖  KPI Definitions"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — FINANCE (+ Cost Breakdown + Stripe Negotiation)
# ══════════════════════════════════════════════════════════════════════════════
with tab_finance:
    st.markdown('<div class="tab-intro">💰 <strong>Finance View</strong> — Revenue performance, margin analysis, and complete cost breakdown across the 3% fee structure (1.8% interchange · 0.2% Stripe · 1.0% Togetherwork). Includes Stripe volume tier analysis for rate negotiation.</div>', unsafe_allow_html=True)

    # ── Volume & Revenue KPIs ─────────────────────────────────────────────────
    st.markdown('<div class="section-header">📦 Volume & Revenue</div>', unsafe_allow_html=True)
    total_tpv   = filtered["total_processing_volume"].sum()
    total_fee   = filtered["total_fee_collected"].sum()
    tw_revenue  = filtered["tw_net_revenue"].sum()
    avg_margin  = filtered["margin"].mean()
    avg_take    = 0.010
    total_txns  = filtered["transaction_count"].sum()

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    kpi_card(c1, "Total Processing Volume", f"${total_tpv/1e6:.1f}M")
    kpi_card(c2, "Total Fees Collected (3%)", f"${total_fee/1e6:.2f}M")
    kpi_card(c3, "TW Net Revenue (1%)", f"${tw_revenue/1e6:.2f}M", tag="After paying interchange + Stripe", good=True)
    kpi_card(c4, "Avg Margin", f"{avg_margin*100:.1f}%")
    kpi_card(c5, "TW Take Rate", "1.00%", tag="of every transaction", good=True)
    kpi_card(c6, "Total Transactions", f"{total_txns:,.0f}")

    c_left, c_right = st.columns(2)
    with c_left:
        m = monthly("total_processing_volume")
        fig = px.area(m, x="month", y="total_processing_volume", color_discrete_sequence=[PALETTE[0]])
        fig.update_traces(fill="tozeroy", line_width=2)
        clayout(fig, "Monthly Total Processing Volume")
        st.plotly_chart(fig, use_container_width=True)
    with c_right:
        rev_m = monthly("tw_net_revenue")
        fee_m = monthly("total_fee_collected")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=fee_m["month"], y=fee_m["total_fee_collected"], name="Total 3% Fee Collected", marker_color=PALETTE[2]))
        fig.add_trace(go.Bar(x=rev_m["month"], y=rev_m["tw_net_revenue"], name="TW Net Revenue (1%)", marker_color=PALETTE[1]))
        fig.update_layout(barmode="overlay")
        clayout(fig, "Fee Collected vs TW Net Revenue")
        st.plotly_chart(fig, use_container_width=True)

    # ── COST BREAKDOWN ────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">💸 Cost Breakdown — Where Every Transaction Dollar Goes</div>', unsafe_allow_html=True)

    total_interchange = filtered["interchange_cost"].sum()
    total_stripe      = filtered["stripe_cost"].sum()
    total_tw_rev      = filtered["tw_net_revenue"].sum()
    total_collected   = filtered["total_fee_collected"].sum()

    # Waterfall KPI cards
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"""
    <div class="kpi-card" style="border-left: 4px solid #e05c6a;">
      <div class="kpi-label">Customer Pays (3.0%)</div>
      <div class="kpi-value">${total_collected/1e6:.2f}M</div>
      <div class="kpi-delta-neg">100% of fees collected</div>
    </div>""", unsafe_allow_html=True)
    c2.markdown(f"""
    <div class="kpi-card" style="border-left: 4px solid #e09a3a;">
      <div class="kpi-label">Card Networks (1.8%)</div>
      <div class="kpi-value">${total_interchange/1e6:.2f}M</div>
      <div class="kpi-delta-neg">Visa / Mastercard interchange</div>
    </div>""", unsafe_allow_html=True)
    c3.markdown(f"""
    <div class="kpi-card" style="border-left: 4px solid #9b6dd1;">
      <div class="kpi-label">Stripe Processor (0.2%)</div>
      <div class="kpi-value">${total_stripe/1e6:.2f}M</div>
      <div class="kpi-delta-neg">Negotiable at volume ↓</div>
    </div>""", unsafe_allow_html=True)
    c4.markdown(f"""
    <div class="kpi-card" style="border-left: 4px solid #4caf87;">
      <div class="kpi-label">Togetherwork Keeps (1.0%)</div>
      <div class="kpi-value">${total_tw_rev/1e6:.2f}M</div>
      <div class="kpi-delta-pos">Net revenue after all costs</div>
    </div>""", unsafe_allow_html=True)

    c_left, c_right = st.columns(2)
    with c_left:
        # Donut chart showing fee distribution
        fig = go.Figure(go.Pie(
            labels=["Card Networks (1.8%)", "Stripe (0.2%)", "Togetherwork (1.0%)"],
            values=[total_interchange, total_stripe, total_tw_rev],
            hole=0.55,
            marker_colors=[PALETTE[3], PALETTE[4], PALETTE[1]],
        ))
        fig.update_traces(textinfo="label+percent", textfont_size=11)
        fig.update_layout(
            title=dict(text="Fee Distribution — How Every 3% Is Split", font=dict(family="DM Serif Display", size=13, color=FONT_COLOR)),
            paper_bgcolor=PAPER_BG, font=dict(family="DM Sans", color=FONT_COLOR),
            height=320, margin=dict(l=10,r=10,t=38,b=10),
            showlegend=False,
            annotations=[dict(text=f"${total_collected/1e6:.1f}M<br>collected", x=0.5, y=0.5, font_size=12, showarrow=False, font_color=FONT_COLOR)]
        )
        st.plotly_chart(fig, use_container_width=True)

    with c_right:
        # Cost breakdown by vertical
        vb = filtered.groupby("vertical").agg(
            interchange=("interchange_cost","sum"),
            stripe=("stripe_cost","sum"),
            tw_rev=("tw_net_revenue","sum"),
        ).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Card Networks (1.8%)", x=vb["vertical"], y=vb["interchange"], marker_color=PALETTE[3]))
        fig.add_trace(go.Bar(name="Stripe (0.2%)",        x=vb["vertical"], y=vb["stripe"],      marker_color=PALETTE[4]))
        fig.add_trace(go.Bar(name="TW Revenue (1.0%)",    x=vb["vertical"], y=vb["tw_rev"],      marker_color=PALETTE[1]))
        fig.update_layout(barmode="stack")
        clayout(fig, "Cost Breakdown by Vertical")
        st.plotly_chart(fig, use_container_width=True)

    # ── STRIPE NEGOTIATION ────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🤝 Stripe Rate Negotiation — Volume Tier Analysis</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box">
      <div class="insight-title">💡 Why This Matters</div>
      <div class="insight-body">
        Stripe's standard rate is 0.2% of TPV. At higher processing volumes, Stripe offers custom pricing.
        Every 0.05% reduction in Stripe fees goes directly to Togetherwork's bottom line.
        This analysis shows current volume trajectory and estimates the savings from a successful negotiation.
      </div>
    </div>""", unsafe_allow_html=True)

    # Volume tiers for negotiation
    ann_tpv = total_tpv * (12 / filtered["month"].nunique()) if filtered["month"].nunique() > 0 else total_tpv

    tiers = [
        ("Standard",  0,          50e6,  0.200, "#e05c6a"),
        ("Growth",    50e6,       150e6, 0.175, "#e09a3a"),
        ("Scale",     150e6,      500e6, 0.150, "#4a6fa5"),
        ("Enterprise",500e6,      1e12,  0.100, "#4caf87"),
    ]

    current_tier = "Standard"
    current_rate = 0.200
    for tier, lo, hi, rate, color in tiers:
        if lo <= ann_tpv < hi:
            current_tier = tier
            current_rate = rate

    savings_potential = (0.200 - current_rate) / 100 * ann_tpv if current_rate < 0.200 else 0

    c1, c2, c3, c4 = st.columns(4)
    kpi_card(c1, "Annualized TPV",         f"${ann_tpv/1e6:.1f}M",    tag=f"Current volume tier basis",  good=True)
    kpi_card(c2, "Current Volume Tier",    current_tier,               tag="Stripe negotiation position", good=current_tier != "Standard")
    kpi_card(c3, "Current Stripe Rate",    f"{current_rate:.3f}%",     tag="of every transaction",        good=current_rate < 0.200)
    kpi_card(c4, "Annual Stripe Cost",     f"${ann_tpv*current_rate/100/1e3:.0f}K", tag="At current rate", good=False)

    c_left, c_right = st.columns(2)
    with c_left:
        # Volume growth toward next tier
        tier_labels = ["Standard\n<$50M", "Growth\n$50-150M", "Scale\n$150-500M", "Enterprise\n>$500M"]
        tier_rates  = [0.200, 0.175, 0.150, 0.100]
        tier_colors = [PALETTE[3] if t == current_tier else PALETTE[0] for t in ["Standard","Growth","Scale","Enterprise"]]
        fig = go.Figure(go.Bar(
            x=tier_labels, y=tier_rates,
            marker_color=tier_colors,
            text=[f"{r:.3f}%" for r in tier_rates],
            textposition="outside",
        ))
        fig.add_hline(y=current_rate, line_dash="dash", line_color=PALETTE[1],
                      annotation_text=f"Current: {current_rate:.3f}%")
        fig.update_yaxes(tickformat=".3f", range=[0, 0.25])
        clayout(fig, "Stripe Rate by Volume Tier — Negotiation Roadmap")
        st.plotly_chart(fig, use_container_width=True)

    with c_right:
        # Monthly Stripe cost trend + savings projection
        ms = filtered.groupby("month")["stripe_cost"].sum().reset_index()
        ms["savings_at_scale"] = filtered.groupby("month")["total_processing_volume"].sum().values * 0.0015
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ms["month"], y=ms["stripe_cost"],
                                 name="Current Stripe Cost (0.2%)", line=dict(color=PALETTE[3], width=2)))
        fig.add_trace(go.Scatter(x=ms["month"], y=ms["savings_at_scale"],
                                 name="Projected at Scale Rate (0.15%)", line=dict(color=PALETTE[1], width=2, dash="dash")))
        clayout(fig, "Stripe Cost: Current vs Projected After Negotiation")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    <div class="insight-box">
      <div class="insight-title">📊 Negotiation Summary</div>
      <div class="insight-body">
        At <strong>${ann_tpv/1e6:.1f}M annualized TPV</strong>, Togetherwork is positioned at the <strong>{current_tier}</strong> tier.
        Moving to the Scale tier ($150M+ TPV) would reduce the Stripe rate from 0.200% to 0.150% —
        saving approximately <strong>${ann_tpv * 0.0005 / 1e3:.0f}K annually</strong> that flows directly to net revenue.
        The key lever: consolidate TPV reporting across all verticals into a single Stripe account to maximize negotiating volume.
      </div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PRODUCT + CLIENT INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
with tab_product:
    st.markdown('<div class="tab-intro">📱 <strong>Product & Client Intelligence</strong> — Subscription health, retention metrics, and client usage profiling. Includes payment engagement scoring and credit/loan eligibility tiers based on processing behavior.</div>', unsafe_allow_html=True)

    # ── Subscription KPIs ─────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🔄 Subscription & Retention</div>', unsafe_allow_html=True)
    avg_t2p       = filtered["trial_to_paid_rate"].mean()
    avg_inv_churn = filtered["involuntary_churn_rate"].mean()
    avg_dunning   = filtered["dunning_recovery_rate"].mean()
    total_mrr     = filtered.groupby("month")["mrr"].sum().mean()
    avg_nrr       = filtered["net_revenue_retention"].mean()

    c1,c2,c3,c4,c5 = st.columns(5)
    kpi_card(c1, "Trial → Paid Rate",     f"{avg_t2p*100:.1f}%",       tag="↑ Growth lever",  good=True)
    kpi_card(c2, "Involuntary Churn",     f"{avg_inv_churn*100:.2f}%", tag="⚠ Monitor",       good=False)
    kpi_card(c3, "Dunning Recovery",      f"{avg_dunning*100:.1f}%",   tag="↑ Revenue save",  good=True)
    kpi_card(c4, "Avg Monthly MRR",       f"${total_mrr/1e3:.1f}K")
    kpi_card(c5, "Net Revenue Retention", f"{avg_nrr*100:.1f}%",       tag="✓ Healthy" if avg_nrr >= 1 else "⚠ Below 100%", good=avg_nrr >= 1)

    c_left, c_right = st.columns(2)
    with c_left:
        mrr_m = filtered.groupby("month")["mrr"].sum().reset_index()
        fig = px.bar(mrr_m, x="month", y="mrr", color_discrete_sequence=[PALETTE[0]])
        clayout(fig, "Monthly Recurring Revenue (MRR)")
        st.plotly_chart(fig, use_container_width=True)
    with c_right:
        nrr_m = monthly("net_revenue_retention","mean")
        fig = px.line(nrr_m, x="month", y="net_revenue_retention", color_discrete_sequence=[PALETTE[4]])
        fig.update_traces(line_width=2)
        fig.add_hline(y=1.0, line_dash="dash", line_color=PALETTE[1], annotation_text="100% NRR target")
        fig.update_yaxes(tickformat=".1%")
        clayout(fig, "Net Revenue Retention Over Time")
        st.plotly_chart(fig, use_container_width=True)

    # ── CLIENT USAGE PROFILING & CREDIT ELIGIBILITY ───────────────────────────
    st.markdown('<div class="section-header">🏦 Client Usage Profiling — Payment Intelligence & Credit Eligibility</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box">
      <div class="insight-title">💡 The Opportunity</div>
      <div class="insight-body">
        Clients who consistently process payments through Togetherwork leave a rich behavioral footprint —
        transaction volume, frequency, payment success rates, and chargeback history.
        This data can power a credit scoring model to offer working capital loans or credit lines
        to high-value clients, creating a new revenue stream beyond payment processing fees.
        This is how Square, Stripe, and PayPal built their lending businesses.
      </div>
    </div>""", unsafe_allow_html=True)

    # Build client profile by vertical
    client_profile = filtered.groupby("vertical").agg(
        total_tpv=("total_processing_volume","sum"),
        avg_txn_count=("transaction_count","mean"),
        avg_success_rate=("payment_success_rate","mean"),
        avg_chargeback=("chargeback_rate","mean"),
        avg_engagement=("engagement_score","mean"),
        avg_mrr=("mrr","mean"),
        months_active=("month","nunique"),
    ).reset_index()

    # Annualize TPV
    client_profile["ann_tpv"] = client_profile["total_tpv"] * (12 / client_profile["months_active"])

    # Credit tier logic
    def credit_tier(row):
        score = row["avg_engagement"]
        cb    = row["avg_chargeback"]
        if score >= 70 and cb < 0.005: return "🏆 Platinum"
        elif score >= 55 and cb < 0.008: return "🥇 Gold"
        elif score >= 40 and cb < 0.012: return "🥈 Silver"
        else: return "⚠️ Watch"

    def credit_line(row):
        # Estimated credit line = 10% of annualized TPV, adjusted for risk
        base = row["ann_tpv"] * 0.10
        if "Platinum" in row["credit_tier"]: return base * 1.5
        elif "Gold" in row["credit_tier"]:   return base * 1.0
        elif "Silver" in row["credit_tier"]: return base * 0.5
        else: return 0

    client_profile["credit_tier"]  = client_profile.apply(credit_tier, axis=1)
    client_profile["credit_line"]  = client_profile.apply(credit_line, axis=1)
    client_profile["engagement_pct"] = client_profile["avg_engagement"].round(1)

    # Credit tier cards
    for _, row in client_profile.iterrows():
        tier_color = {"🏆 Platinum": "#4caf87", "🥇 Gold": "#e09a3a", "🥈 Silver": "#8a9ab0", "⚠️ Watch": "#e05c6a"}.get(row["credit_tier"], "#4a6fa5")
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.markdown(f"""<div class="credit-card"><div class="credit-tier">Vertical</div>
        <div class="credit-amount" style="font-size:1.2rem;">{row['vertical']}</div></div>""", unsafe_allow_html=True)
        c2.markdown(f"""<div class="credit-card"><div class="credit-tier">Engagement Score</div>
        <div class="credit-amount">{row['engagement_pct']}</div>
        <div class="credit-sub">/ 100 composite score</div></div>""", unsafe_allow_html=True)
        c3.markdown(f"""<div class="credit-card"><div class="credit-tier">Annualized TPV</div>
        <div class="credit-amount">${row['ann_tpv']/1e6:.1f}M</div></div>""", unsafe_allow_html=True)
        c4.markdown(f"""<div class="credit-card" style="border-left: 3px solid {tier_color};">
        <div class="credit-tier">Credit Tier</div>
        <div class="credit-amount" style="font-size:1.1rem; color:{tier_color};">{row['credit_tier']}</div></div>""", unsafe_allow_html=True)
        c5.markdown(f"""<div class="credit-card" style="border-left: 3px solid #4caf87;">
        <div class="credit-tier">Est. Credit Line</div>
        <div class="credit-amount" style="color:#4caf87;">${row['credit_line']/1e3:.0f}K</div>
        <div class="credit-sub">Working capital offer</div></div>""", unsafe_allow_html=True)
        st.markdown("")

    c_left, c_right = st.columns(2)
    with c_left:
        fig = px.scatter(client_profile, x="ann_tpv", y="engagement_pct",
                         size="credit_line", color="credit_tier", text="vertical",
                         color_discrete_sequence=PALETTE,
                         labels={"ann_tpv":"Annualized TPV ($)","engagement_pct":"Engagement Score"})
        fig.update_traces(textposition="top center")
        clayout(fig, "Client Engagement Score vs TPV — Credit Opportunity Map", height=340)
        st.plotly_chart(fig, use_container_width=True)

    with c_right:
        fig = px.bar(client_profile.sort_values("credit_line", ascending=True),
                     x="credit_line", y="vertical", orientation="h",
                     color="credit_tier", color_discrete_sequence=PALETTE,
                     labels={"credit_line":"Estimated Credit Line ($)","vertical":"Vertical"})
        fig.update_layout(showlegend=True)
        clayout(fig, "Estimated Credit Line by Vertical", height=340)
        st.plotly_chart(fig, use_container_width=True)

    total_credit_opportunity = client_profile["credit_line"].sum()
    st.markdown(f"""
    <div class="insight-box">
      <div class="insight-title">📊 Credit Portfolio Summary</div>
      <div class="insight-body">
        Total estimated credit line opportunity across all verticals: <strong>${total_credit_opportunity/1e6:.1f}M</strong>.
        Platinum and Gold tier clients — those with high engagement scores and low chargeback rates —
        represent the lowest-risk lending targets. The engagement score model uses transaction frequency (35%),
        TPV consistency (35%), payment success rate (20%), and chargeback health (10%) as inputs.
        Real implementation would layer in months of tenure, seasonal patterns, and dispute history.
      </div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab_ops:
    st.markdown('<div class="tab-intro">⚙️ <strong>Operations View</strong> — Risk monitoring, payment performance, anomaly detection, and system reliability. Designed to surface issues before they become card network penalties.</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">⚠️ Risk & Failures</div>', unsafe_allow_html=True)
    avg_auth  = filtered["authorization_rate"].mean()
    avg_dec   = filtered["decline_rate"].mean()
    avg_fraud = filtered["fraud_rate"].mean()
    avg_cb    = filtered["chargeback_rate"].mean()
    avg_ref   = filtered["refund_rate"].mean()

    c1,c2,c3,c4,c5 = st.columns(5)
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
        fig.add_hline(y=1.0, line_dash="dot", line_color=PALETTE[3], annotation_text="1% card network warning")
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

    st.markdown('<div class="section-header">⚙️ Performance & Reliability</div>', unsafe_allow_html=True)
    avg_success  = filtered["payment_success_rate"].mean()
    avg_latency  = filtered["latency_ms"].mean()
    avg_uptime   = filtered["uptime"].mean()
    avg_recovery = filtered["failed_payment_recovery_rate"].mean()

    c1,c2,c3,c4 = st.columns(4)
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
        ms2 = monthly("payment_success_rate","mean")
        fig = px.area(ms2, x="month", y="payment_success_rate", color_discrete_sequence=[PALETTE[1]])
        fig.update_traces(fill="tozeroy", line_width=2)
        fig.update_yaxes(tickformat=".2%", range=[0.9, 1.0])
        clayout(fig, "Monthly Payment Success Rate")
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — KPI DEFINITIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab_defs:
    st.markdown('<div class="tab-intro">📖 <strong>KPI Definitions</strong> — Standardized definitions for all metrics including cost breakdown, Stripe negotiation, and client credit scoring. Filter by category.</div>', unsafe_allow_html=True)

    categories  = ["All"] + sorted(kpi_df["Category"].unique().tolist())
    search_cat  = st.selectbox("Filter by Category", categories)
    search_term = st.text_input("Search by KPI name or keyword", placeholder="e.g. interchange, credit, stripe, chargeback...")

    display_df = kpi_df.copy()
    if search_cat != "All":
        display_df = display_df[display_df["Category"] == search_cat]
    if search_term:
        mask = (display_df["KPI Name"].str.contains(search_term, case=False) |
                display_df["Definition"].str.contains(search_term, case=False))
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
    'Payments Analytics Dashboard · Finance · Product & Client Intelligence · Operations · '
    'Fee Structure: 3.0% charged → 1.8% interchange · 0.2% Stripe · 1.0% Togetherwork · '
    'Built with Streamlit & Plotly · Synthetic Data 2023–2024'
    '</p>', unsafe_allow_html=True
)
