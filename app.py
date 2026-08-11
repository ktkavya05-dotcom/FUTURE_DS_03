"""Streamlit funnel intelligence dashboard for e-commerce event data.

Run: streamlit run app.py
"""
from pathlib import Path
import hashlib

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Flowline | Funnel Intelligence", page_icon="↗", layout="wide")

DATA_FILE = Path(__file__).with_name("2019-Nov.csv")
EVENT_COLUMNS = ["event_time", "event_type", "price", "user_id"]

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Nunito:wght@500;600;700;800&display=swap');
  :root { --ink:#101014; --blue:#353eaf; --yellow:#ffd233; --coral:#f15b64; --cream:#fff8eb; }
  .stApp { background:var(--blue); color:var(--ink); font-family:'Nunito',sans-serif; }
  .stApp::before {content:""; position:fixed; inset:0; pointer-events:none; opacity:.17; background-image:radial-gradient(#fff 1px,transparent 1px),radial-gradient(#fff 1px,transparent 1px); background-position:0 0,10px 10px; background-size:22px 22px; mix-blend-mode:overlay;}
  .block-container {max-width: 1420px; padding-top: 1.5rem; padding-bottom: 3rem;}
  [data-testid="stSidebar"] {background:#111116; border-right:5px solid var(--yellow);}
  [data-testid="stSidebar"] * {color:#fff8eb !important;}
  [data-testid="stSidebar"] [data-baseweb="slider"] div {color:var(--yellow) !important;}
  [data-testid="stSidebar"] .stSlider div[data-baseweb="slider"] div[role="slider"] {background:var(--yellow) !important;}
  [data-testid="stMetric"] {background:var(--cream); border:3px solid var(--ink); border-radius:9px 13px 10px 14px; box-shadow:5px 6px 0 #111116; padding:15px 16px;}
  [data-testid="stMetricLabel"] {font-size:11px; font-weight:800; color:#433c31; letter-spacing:.03em;}
  [data-testid="stMetricValue"] {font-family:'Baloo 2',sans-serif; font-size:28px; font-weight:800; color:var(--ink);}
  [data-testid="stMetricDelta"] {font-weight:800;}
  .headline {display:inline-block; background:#101014; color:var(--yellow); padding:6px 15px 8px; border-radius:10px 12px 9px 11px; font-family:'Baloo 2',sans-serif; font-size:31px; font-weight:800; letter-spacing:-.6px; margin-bottom:0; box-shadow:4px 4px 0 rgba(0,0,0,.28);}
  .subtitle {color:#fff8eb; font-weight:700; margin-top:12px; margin-bottom:16px;}
  .callout {background:#ffd233; border:3px solid #111116; border-radius:14px 11px 15px 10px; box-shadow:5px 6px 0 #111116; padding:13px 16px; color:#201d18; margin:12px 0 25px; font-weight:600;}
  .section-label {display:inline-block;background:var(--yellow);border:3px solid var(--ink); border-radius:7px 9px 7px 10px;box-shadow:3px 3px 0 #111116;color:#171515;font-family:'Baloo 2',sans-serif;font-size:17px;font-weight:800; padding:2px 10px; margin:20px 0 4px;}
  .tiny {color:#fff8eb; font-size:11px; font-weight:700; margin-bottom:7px;}
  .task-pill {display:table;margin:0 auto 15px;background:var(--yellow);border:3px solid var(--ink);border-radius:0 0 12px 12px;padding:2px 17px 5px;font-family:'Baloo 2',sans-serif;font-size:23px;font-weight:800;box-shadow:4px 4px 0 #111116;}
  .brief {background:var(--cream);border:4px solid var(--ink);border-radius:15px 11px 16px 12px;box-shadow:7px 8px 0 #111116;padding:17px 20px 14px;margin:4px 0 28px;}
  .brief-title {font-family:'Baloo 2',sans-serif;font-size:19px;font-weight:800;margin:0 0 7px;color:#191713;}
  .brief p {margin:7px 0;color:#29251e;font-size:13px;line-height:1.48;font-weight:650;}
  .brief strong {color:var(--coral);}
  [data-testid="stDataFrame"], [data-testid="stPlotlyChart"] {background:var(--cream); border:3px solid var(--ink); border-radius:12px 9px 14px 10px; box-shadow:5px 6px 0 #111116; overflow:hidden;}
  .stButton button {background:var(--yellow); color:#111116; border:2px solid #111116; border-radius:8px; box-shadow:3px 3px 0 #111116; font-weight:800;}
  .stButton button:hover {background:#fff0a0; border-color:#111116; color:#111116; transform:translate(1px,1px); box-shadow:2px 2px 0 #111116;}
  hr {border-color:rgba(255,248,235,.35);}
  [data-testid="stCaptionContainer"] {color:#fff8eb !important;}
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_events(path: str, row_limit: int) -> pd.DataFrame:
    """Read only the requested prefix; the source file is ~9GB."""
    data = pd.read_csv(path, usecols=EVENT_COLUMNS, nrows=row_limit)
    data["event_time"] = pd.to_datetime(data["event_time"], utc=True, errors="coerce")
    data = data.dropna(subset=["event_time", "event_type", "user_id"])
    return data[data["event_type"].isin(["view", "cart", "purchase"])]


def model_channel(user_id: int) -> str:
    """Deterministic illustrative segmentation when source attribution is absent."""
    buckets = ["Organic search", "Paid search", "Social", "Email / CRM", "Referral"]
    digest = hashlib.blake2b(str(user_id).encode(), digest_size=2).digest()
    number = int.from_bytes(digest, "big") % 100
    return buckets[0] if number < 30 else buckets[1] if number < 53 else buckets[2] if number < 78 else buckets[3] if number < 88 else buckets[4]


def funnel_counts(data: pd.DataFrame) -> pd.DataFrame:
    result = data.groupby("event_type")["user_id"].nunique()
    views, carts, purchases = (int(result.get(x, 0)) for x in ["view", "cart", "purchase"])
    return pd.DataFrame({"Stage": ["Product views", "Added to cart", "Customers"], "Users": [views, carts, purchases]})


def rate(numerator: int, denominator: int) -> float:
    return numerator / denominator * 100 if denominator else 0.0


with st.sidebar:
    st.title("💬 Flowline")
    st.caption("FUNNEL INTELLIGENCE")
    st.divider()
    st.subheader("Data controls")
    if not DATA_FILE.exists():
        st.error("2019-Nov.csv was not found beside app.py.")
        st.stop()
    rows = st.select_slider("Rows to analyze", [100_000, 250_000, 500_000, 1_000_000], value=500_000,
                           help="The source is about 9GB. A sample keeps the app responsive.")
    st.caption("Reading the first rows of the event stream. Use a representative extract for production reporting.")
    st.divider()
    st.subheader("Funnel definition")
    st.caption("Visitor = view\n\nQualified lead = cart\n\nCustomer = purchase")
    st.divider()
    st.caption("Source: 2019-Nov.csv\n\nEvent-level e-commerce data")

try:
    with st.spinner("Preparing your funnel data…"):
        events = load_events(str(DATA_FILE), rows)
except Exception as exc:
    st.error(f"Could not read the event data: {exc}")
    st.stop()

dates = events["event_time"].dt.date
min_date, max_date = dates.min(), dates.max()
selected_dates = st.sidebar.date_input("Date range in sample", value=(min_date, max_date), min_value=min_date, max_value=max_date)
if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    events = events[(dates >= selected_dates[0]) & (dates <= selected_dates[1])]

funnel = funnel_counts(events)
viewers, leads, customers = funnel["Users"].tolist()
cart_rate, customer_rate, checkout_rate = rate(leads, viewers), rate(customers, viewers), rate(customers, leads)
revenue = events.loc[events.event_type == "purchase", "price"].sum()

st.markdown('<div class="task-pill">Task 3</div><div class="headline">Marketing Funnel & Conversion Performance Analysis</div><div class="subtitle">See where shoppers leave, which audiences have intent, and where to focus next.</div>', unsafe_allow_html=True)
st.markdown("""
<div class="brief">
  <div class="brief-title">📌 Project brief</div>
  <p>🔹 <strong>Task:</strong> Analyze marketing funnel data to identify conversion drop-offs, channel performance, and opportunities to improve lead-to-customer conversion.</p>
  <p>🔹 <strong>Tools:</strong> Excel / Google Sheets / Power BI / Tableau / Python — use the tool best suited for funnel analysis.</p>
  <p>🔹 <strong>Skills Gained:</strong> Funnel analysis, conversion metrics, growth analytics, and performance optimization.</p>
  <p>🔹 <strong>Deliverable:</strong> A funnel performance dashboard or analysis report with key drop-off insights and actionable recommendations to improve conversions.</p>
</div>
""", unsafe_allow_html=True)
st.markdown(f'<div class="callout">💡 <b>Current focus:</b> only <b>{cart_rate:.1f}%</b> of visitors add an item to cart — the product-to-cart moment is the biggest conversion opportunity.</div>', unsafe_allow_html=True)

metrics = st.columns(4)
metrics[0].metric("PRODUCT VIEWERS", f"{viewers:,}", help="Unique users who viewed a product")
metrics[1].metric("QUALIFIED LEADS · CARTS", f"{leads:,}", f"{cart_rate:.1f}% of viewers")
metrics[2].metric("CUSTOMERS · PURCHASES", f"{customers:,}", f"{customer_rate:.1f}% of viewers")
metrics[3].metric("PURCHASE REVENUE", f"₹{revenue:,.0f}", help="Sum of recorded purchase prices in the selected sample")

left, right = st.columns([1.22, 1])
with left:
    st.markdown('<div class="section-label">Conversion trend</div><div class="tiny">Daily unique-user view-to-purchase conversion</div>', unsafe_allow_html=True)
    daily = events.assign(day=events.event_time.dt.date).pivot_table(index="day", columns="event_type", values="user_id", aggfunc=pd.Series.nunique, fill_value=0).reset_index()
    for column in ["view", "purchase"]:
        if column not in daily: daily[column] = 0
    daily["Conversion rate"] = daily.apply(lambda r: rate(r["purchase"], r["view"]), axis=1)
    fig = px.area(daily, x="day", y="Conversion rate", markers=True, color_discrete_sequence=["#1c9a74"])
    fig.add_hline(y=customer_rate, line_dash="dot", line_color="#99aaa3", annotation_text="Sample average", annotation_position="top left")
    fig.update_layout(height=310, margin=dict(l=0, r=5, t=12, b=0), plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", yaxis_title="Conversion (%)", xaxis_title="", showlegend=False)
    fig.update_yaxes(gridcolor="#edf1ee", zeroline=False)
    fig.update_xaxes(gridcolor="#ffffff")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown('<div class="section-label">Funnel drop-off</div><div class="tiny">Unique users at each event stage</div>', unsafe_allow_html=True)
    fig = go.Figure(go.Funnel(y=funnel.Stage, x=funnel.Users, textinfo="value+percent initial", marker={"color":["#b8e673", "#f5c953", "#1c9a74"]}))
    fig.update_layout(height=310, margin=dict(l=0, r=0, t=22, b=0), paper_bgcolor="#ffffff", plot_bgcolor="#ffffff", font={"family":"Arial", "color":"#243b34"})
    st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="section-label">Channel quality</div><div class="tiny">Illustrative modeled attribution — the raw file has no source/channel column.</div>', unsafe_allow_html=True)
channel_events = events.copy()
channel_events["Channel"] = channel_events.user_id.map(model_channel)
channel_pivot = channel_events.pivot_table(index="Channel", columns="event_type", values="user_id", aggfunc=pd.Series.nunique, fill_value=0)
for event in ["view", "cart", "purchase"]:
    if event not in channel_pivot: channel_pivot[event] = 0
channel_pivot["Lead rate"] = (channel_pivot["cart"] / channel_pivot["view"] * 100).fillna(0)
channel_pivot["Customer rate"] = (channel_pivot["purchase"] / channel_pivot["view"] * 100).fillna(0)
channel_display = channel_pivot.reset_index().rename(columns={"view":"Visitors", "cart":"Leads", "purchase":"Customers"})
channel_display = channel_display.sort_values("Customer rate", ascending=False)

ch_left, ch_right = st.columns([.9, 1.1])
with ch_left:
    st.dataframe(channel_display[["Channel", "Visitors", "Leads", "Customers", "Lead rate", "Customer rate"]], hide_index=True, use_container_width=True,
                 column_config={"Lead rate":st.column_config.NumberColumn(format="%.1f%%"), "Customer rate":st.column_config.NumberColumn(format="%.1f%%")})
with ch_right:
    fig = px.bar(channel_display, x="Channel", y="Customer rate", color="Customer rate", color_continuous_scale=["#d9efe1", "#1c9a74"])
    fig.update_layout(height=265, margin=dict(l=0,r=0,t=10,b=0), coloraxis_showscale=False, yaxis_title="Customer rate (%)", xaxis_title="", paper_bgcolor="#ffffff", plot_bgcolor="#ffffff")
    fig.update_yaxes(gridcolor="#edf1ee")
    st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="section-label">Recommended next moves</div>', unsafe_allow_html=True)
top_channel = channel_display.iloc[0]
recommendations = [
    ("Improve the product-to-cart moment", f"{100-cart_rate:.1f}% of viewers do not add an item to cart. Test clearer delivery/returns copy, product trust signals, and a sticky mobile add-to-cart control."),
    ("Recover cart abandoners", f"{100-checkout_rate:.1f}% of cart users do not purchase. Trigger a short cart-recovery sequence and reduce guest-checkout friction."),
    ("Prioritize high-intent acquisition", f"In the modeled channel view, {top_channel['Channel']} leads at {top_channel['Customer rate']:.1f}% customer conversion. Validate this with actual UTM data before shifting spend."),
]
for i, (title, description) in enumerate(recommendations, 1):
    st.markdown(f"**{i}. {title}**  \n{description}")

st.divider()
st.caption(f"Analysis uses {len(events):,} qualifying events from the selected sample. For accurate campaign reporting, enrich the raw events with UTM/channel, landing-page, and checkout-step data.")
