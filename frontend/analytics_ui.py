import streamlit as st
from datetime import datetime
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

API_URL = "http://localhost:8000"

CATEGORY_COLORS_LIGHT = {
    "🏠 Rent": "#3498db",
    "🍔 Food": "#2ecc71",
    "🛍️ Shopping": "#e67e22",
    "🎬 Entertainment": "#9b59b6",
    "📌 Other": "#7f8c8d"
}

CATEGORY_COLORS_DARK = {
    "🏠 Rent": "#2980b9",
    "🍔 Food": "#27ae60",
    "🛍️ Shopping": "#d35400",
    "🎬 Entertainment": "#8e44ad",
    "📌 Other": "#95a5a6"
}


def _is_dark_theme(theme):
    if theme is None:
        return False
    t = str(theme).lower()
    return "dark" in t or "🌙" in t or t == "true"


def analytics_tab(theme="Light"):
    dark = _is_dark_theme(theme)

    if dark:
        css = """
        <style>
        .analytics-wrapper { background: linear-gradient(135deg,#0f1724 0%,#1f2a44 50%,#2b3750 100%);padding:18px;border-radius:14px;color:#ecf0f1;}
        .analytics-wrapper table.summary th,.analytics-wrapper table.summary td{border:1px solid rgba(226,232,240,0.06);padding:8px;}
        </style>
        """
    else:
        css = """
        <style>
        .analytics-wrapper { background: linear-gradient(135deg,#f8fafc 0%,#eef2ff 50%,#fffaf0 100%);padding:18px;border-radius:14px;color:#1f2937;}
        .analytics-wrapper table.summary th,.analytics-wrapper table.summary td{border:1px solid rgba(55,65,81,0.12);padding:8px;}
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)
    st.markdown("<div class='analytics-wrapper'>", unsafe_allow_html=True)

    st.markdown("<h1>📊 Expense Analytics</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date", datetime(2024, 8, 1))
    with col2:
        end_date = st.date_input("End date", datetime.today())

    if "analytics_data" not in st.session_state:
        st.session_state.analytics_data = None
        st.session_state.start_date = None
        st.session_state.end_date = None

    if st.button("🔍 Get Analytics"):
        payload = {"start_date": start_date.strftime("%Y-%m-%d"), "end_date": end_date.strftime("%Y-%m-%d")}
        try:
            r = requests.post(f"{API_URL}/analytics/", json=payload, timeout=10)
            r.raise_for_status()
            st.session_state.analytics_data = r.json()
            st.session_state.start_date = start_date
            st.session_state.end_date = end_date
            st.success("✅ Analytics data loaded")
        except Exception as e:
            st.error(f"❌ Failed to load analytics: {e}")
            st.markdown("</div>", unsafe_allow_html=True)
            return

    data = st.session_state.analytics_data
    s_date = st.session_state.start_date
    e_date = st.session_state.end_date
    if not data:
        st.info("ℹ️ No analytics loaded yet. Click 'Get Analytics' to fetch data.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    df = pd.DataFrame({
        "Category": list(data.keys()),
        "Total": [data[k]["total"] for k in data],
        "Percentage": [data[k]["percentage"] for k in data]
    }).sort_values(by="Percentage", ascending=False).reset_index(drop=True)

    if dark:
        template = "plotly_dark"
        colors = CATEGORY_COLORS_DARK
    else:
        template = "plotly_white"
        colors = CATEGORY_COLORS_LIGHT

    df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0)
    total_exp = df["Total"].sum()
    top_cat = df["Category"].iloc[df["Total"].idxmax()] if len(df) > 0 else "—"
    avg_day = total_exp / max(((e_date - s_date).days + 1), 1)

    c1, c2, c3 = st.columns(3)
    c1.metric("💵 Total Spent", f"{total_exp:.2f}")
    c2.metric("📌 Top Category", top_cat)
    c3.metric("📅 Avg. per Day", f"{avg_day:.2f}")

    st.subheader("📊 Expense Breakdown by Category")
    chart_type = st.radio("Choose Chart Type", ["Bar Chart", "Pie Chart"], horizontal=True, key="chart_type")

    if chart_type == "Bar Chart":
        df_bar = df.sort_values("Total", ascending=True)
        fig = px.bar(df_bar, x="Total", y="Category", text="Total", color="Category",
                     orientation="h", color_discrete_map=colors, template=template)
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
    else:
        df_pie = df[df["Total"] > 0].copy()
        if df_pie.empty:
            st.warning("⚠️ No positive totals available for Pie Chart.")
        else:
            fig = go.Figure(data=[go.Pie(labels=df_pie["Category"], values=df_pie["Total"], hole=0.35,
                                         marker=dict(colors=[colors.get(c, '#888') for c in df_pie["Category"]]))])
            fig.update_layout(template=template, title_text="Expenses Distribution")
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("📑 Detailed Summary")
    df_display = df.copy()
    df_display["Total"] = df_display["Total"].map("{:.2f}".format)
    df_display["Percentage"] = df_display["Percentage"].map("{:.2f}".format)
    df_display["Category"] = df_display["Category"].apply(lambda c: f"<span style='color:{colors.get(c, '#000')};'>●</span> {c}")
    st.markdown(df_display.to_html(escape=False, index=False, classes='summary'), unsafe_allow_html=True)

    st.subheader("📂 Export Summary Data")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Summary (CSV)", data=csv, file_name="expense_summary.csv", mime="text/csv")

    try:
        import xlsxwriter
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Summary")
        st.download_button("⬇️ Download Summary (Excel)", data=buf.getvalue(),
                           file_name="expense_summary.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except ModuleNotFoundError:
        st.info("ℹ️ Install `xlsxwriter` to enable Excel export.")

    st.markdown("</div>", unsafe_allow_html=True)
