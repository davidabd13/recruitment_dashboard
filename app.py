import streamlit as st
import pandas as pd
import plotly.express as px

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Recruitment Fulfillment Analysis",
    layout="wide"
)

# ======================================================
# POWER BI DARK THEME
# ======================================================
st.markdown("""
<style>
.stApp { background-color: #5c5c5c; }

h1 { font-size: 26px; font-weight: 600; }

div[data-testid="metric-container"] {
    background-color: #a1a1a1;
    padding: 18px;
    border-radius: 8px;
}

section[data-testid="stSidebar"] {
    background-color: #a1a1a1;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# LOAD DATA
# ======================================================
@st.cache_data
def load_data():
    return pd.read_excel("data/DB_BI_AMK_AKP.xlsx")

df = load_data()

# ======================================================
# SIDEBAR FILTER
# ======================================================
st.sidebar.title("FILTER")

def select_filter(label, column):
    options = ["All"] + sorted(df[column].dropna().unique())
    return st.sidebar.selectbox(label, options)

filters = {
    "Agency": select_filter("AGENCY", "Agency"),
    "Principle": select_filter("PRINCIPLES", "Principle"),
    "Area": select_filter("AREA", "Area"),
    "Job Title": select_filter("JOB TITLE", "Job Title"),
    "Regional": select_filter("REGIONAL", "Regional"),
    "Status Quota": select_filter("STATUS QUOTA", "Status Quota"),
}

filtered = df.copy()
for col, val in filters.items():
    if val != "All":
        filtered = filtered[filtered[col] == val]

# ======================================================
# KPI SECTION
# ======================================================
st.title("RECRUITMENT FULFILLMENT ANALYSIS")

def fulfillment(data):
    o = (data["Recruitment Status"] == "OPEN").sum()
    r = (data["Recruitment Status"] == "RECRUIT").sum()
    return (1-(r / (r+o)) * 100) if o > 0 else 0

amk = filtered[filtered["Agency"] == "AMK"]
akp = filtered[filtered["Agency"] == "AKP"]

c1, c2, c3 = st.columns(3)
c1.metric("FULFILLMENT %", f"{fulfillment(filtered):.1f}%")
c2.metric("AMK Fulfillment %", f"{fulfillment(amk):.1f}%")
c3.metric("AKP Fulfillment %", f"{fulfillment(akp):.1f}%")

# ======================================================
# CHART 1: RECRUIT vs OPEN BY PRINCIPLE (POWER BI STYLE)
# ======================================================
st.markdown("### Recruitment Overview")

# =============================
# DATA PREPARATION
# =============================
principle_chart = (
    filtered
    .groupby(["Principle", "Recruitment Status"])
    .size()
    .reset_index(name="Count")
)

# Urutkan Principle berdasarkan total Count
order = (
    principle_chart
    .groupby("Principle")["Count"]
    .sum()
    .sort_values(ascending=False)
    .index
)

# =============================
# DINAMIC WIDTH (BAR LEBIH BESAR)
# =============================
num_principle = len(order)
chart_width = max(1600, num_principle * 140)  # 140px / principle

# =============================
# BUILD CHART
# =============================
fig1 = px.bar(
    principle_chart,
    x="Principle",
    y="Count",
    color="Recruitment Status",
    text="Count",
    barmode="group",
    category_orders={"Principle": order},
    color_discrete_map={
        "OPEN": "#1F77B4",
        "RECRUIT": "#4FC3F7"
    }
)

# =============================
# BAR & TEXT STYLE
# =============================
fig1.update_traces(
    textposition="outside",
    textfont_size=12,
    cliponaxis=False
)

# =============================
# LAYOUT (POWER BI FEEL)
# =============================
fig1.update_layout(
    autosize=False,
    width=chart_width,
    height=520,
    bargap=0.04,          # bar lebih tebal
    bargroupgap=0.02,
    plot_bgcolor="#2e2d2d",
    paper_bgcolor="#2e2d2d",
    title="RECRUIT vs OPEN by Principle",
    title_font_size=18,
    legend_title_text="",
    xaxis=dict(
        title="Principle",
        tickangle=-30,     # miring ringan (tidak tabrakan)
        tickfont=dict(size=11),
        automargin=True,
        showgrid=False
    ),
    yaxis=dict(
        title="Count",
        showgrid=True,
        gridcolor="#444"
    ),
    margin=dict(t=60, b=150)
)

# =============================
# SCROLL CONTAINER
# =============================
st.markdown(
    """
    <div style="
        overflow-x:auto;
        overflow-y:hidden;
        padding-bottom:12px;
        border-bottom:1px solid #444;
        white-space:nowrap;
    ">
    """,
    unsafe_allow_html=True
)

st.plotly_chart(
    fig1,
    use_container_width=False,
    config={
        "responsive": False,
        "displaylogo": False
    }
)

st.markdown("</div>", unsafe_allow_html=True)
st.caption("⬅ Scroll horizontally to explore all principles ➡")


# ======================================================
# CHART 2 & 3: REGIONAL
# ======================================================
st.markdown("### Fulfillment by Region")

def regional_chart(data, title):
    temp = (
        data
        .groupby(["Regional", "Recruitment Status"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    temp["Fulfillment %"] = (
        temp.get("RECRUIT", 0) /
        (temp.get("OPEN", 0) + temp.get("RECRUIT", 0))
    ) * 100

    fig = px.bar(
        temp,
        x="Fulfillment %",
        y="Regional",
        orientation="h",
        text=temp["Fulfillment %"].round(1).astype(str) + "%",
        color_discrete_sequence=["#1F77B4"],
        title=title
    )

    fig.update_layout(
        plot_bgcolor="#2e2d2d",
        paper_bgcolor="#2e2d2d",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        title_font_size=16
    )

    fig.update_traces(textposition="inside")
    return fig

l, r = st.columns(2)
l.plotly_chart(regional_chart(amk, "REGION – AMK"), use_container_width=True)
r.plotly_chart(regional_chart(akp, "REGION – AKP"), use_container_width=True)
