import streamlit as st
from add_update_ui import add_update_tab
from analytics_ui import analytics_tab, CATEGORY_COLORS_LIGHT, CATEGORY_COLORS_DARK
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- Page config ---
st.set_page_config(page_title="Expense Manager", page_icon="💰", layout="wide")

API_URL = "http://localhost:8000"

# Sidebar
st.sidebar.title("💰 Expense Manager")
st.sidebar.markdown("Track and analyze your expenses easily.")

menu = st.sidebar.radio("Navigation", ["🏠 Home", "📝 Add/Update", "📊 Analytics"])

# Theme selector
theme = st.sidebar.radio("Theme", ["Light", "Dark"], index=0)

# Theme CSS — updated button styling fix
if theme == "Light":
    st.markdown("""
    <style>
        .main {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9f0f7 100%);
            color: #222 !important;
        }
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            color: #222 !important;
        }
        [data-testid="stSidebar"] * {
            color: #222 !important;
        }
        h1, h2, h3, p, label {
            color: #222 !important;
        }
        .stMetric { background: #fff; color: #222; }
        .footer { color: #222 !important; }

        /* ✅ Light mode buttons: light background + dark text */
        .stButton>button, button[type="submit"], .stDownloadButton>button {
            background-color: #f3f4f6 !important;
            color: #111 !important;
            border: 1px solid #d1d5db !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
        }
        .stButton>button:hover, button[type="submit"]:hover, .stDownloadButton>button:hover {
            background-color: #e5e7eb !important;
            color: #000 !important;
            border-color: #9ca3af !important;
        }

        /* Tables */
        table, th, td {
            border: 1px solid rgba(55,65,81,0.12) !important;
        }
        .streamlit-expanderHeader { color: #111 !important; }
        .js-plotly-plot .plotly .legend { color: #111 !important; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .main {
            background: linear-gradient(135deg, #0f1724 0%, #1f2a44 100%);
            color: #ecf0f1 !important;
        }
        [data-testid="stSidebar"] {
            background-color: #111827 !important;
            color: #ecf0f1 !important;
        }
        [data-testid="stSidebar"] * {
            color: #ecf0f1 !important;
        }
        h1, h2, h3, p, label {
            color: #ecf0f1 !important;
        }
        .stMetric { background: #16324a; color: #ecf0f1; }
        .footer { color: #cbd5e1 !important; }

        /* ✅ Dark mode buttons: dark background + white text */
        .stButton>button, button[type="submit"], .stDownloadButton>button {
            background-color: #1e293b !important;
            color: #f9fafb !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
        }
        .stButton>button:hover, button[type="submit"]:hover, .stDownloadButton>button:hover {
            background-color: #334155 !important;
            color: #fff !important;
            border-color: #475569 !important;
        }

        /* Dark mode table border subtle but visible */
        table, th, td {
            border: 1px solid rgba(226,232,240,0.06) !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Home dashboard
if menu == "🏠 Home":
    st.title("📊 Expense Dashboard")
    start_date = datetime.today() - timedelta(days=7)
    end_date = datetime.today()
    payload = {"start_date": start_date.strftime("%Y-%m-%d"), "end_date": end_date.strftime("%Y-%m-%d")}

    try:
        resp = requests.post(f"{API_URL}/analytics/", json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        st.error(f"⚠️ Failed to load analytics: {e}")
        data = {}

    if data:
        df = pd.DataFrame({
            "Category": list(data.keys()),
            "Total": [data[c]["total"] for c in data],
            "Percentage": [data[c]["percentage"] for c in data]
        })
        df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0)
        total_expense = df["Total"].sum()
        if not df.empty:
            top_category = df.iloc[df["Total"].idxmax()]["Category"]
        else:
            top_category = "—"
        avg = total_expense / max(((end_date - start_date).days + 1), 1)

        m1, m2, m3 = st.columns(3)
        m1.metric("💵 Total (7 days)", f"{total_expense:.2f}")
        m2.metric("📌 Top Category", top_category)
        m3.metric("📅 Avg. per Day", f"{avg:.2f}")

        # charts theme/colors
        if theme == "Dark":
            ct = "plotly_dark"
            colors = CATEGORY_COLORS_DARK
        else:
            ct = "plotly"
            colors = CATEGORY_COLORS_LIGHT

        st.subheader("Spending Breakdown (Last 7 Days)")
        fig = px.bar(df, x="Category", y="Total", text="Total", color="Category",
                     color_discrete_map=colors, template=ct)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No analytics data available for the last 7 days.")

elif menu == "📝 Add/Update":
    add_update_tab(theme=theme)

elif menu == "📊 Analytics":
    analytics_tab(theme if theme == "Dark" else "🌞 Light")

st.markdown("<div style='text-align:center; color:gray; font-size:14px;'>© 2025 Saurabh Mhamunkar | Built with ❤️ using Streamlit & FastAPI</div>", unsafe_allow_html=True)

