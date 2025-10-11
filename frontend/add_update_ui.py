import streamlit as st
from datetime import datetime
import requests

API_URL = "http://localhost:8000"

def add_update_tab(theme="Light"):
    st.title("📝 Add / Update Expenses")
    selected_date = st.date_input("Select Date", datetime.today())

    try:
        resp = requests.get(f"{API_URL}/expenses/{selected_date}", timeout=10)
        resp.raise_for_status()
        existing_expenses = resp.json()
    except Exception:
        st.error("⚠️ Failed to retrieve expenses for selected date.")
        existing_expenses = []

    categories = ["🏠 Rent", "🍔 Food", "🛍️ Shopping", "🎬 Entertainment", "📌 Other"]

    # Wrapper for visible borders
    st.markdown("""
    <style>
    .add-update-wrapper table, .add-update-wrapper th, .add-update-wrapper td {
        border: 1px solid rgba(55,65,81,0.12); border-collapse: collapse; padding: 6px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='add-update-wrapper'>", unsafe_allow_html=True)

    if existing_expenses:
        rows = "".join([
            f"<tr><td>{e.get('category','')}</td><td>{e.get('amount',0)}</td><td>{e.get('notes','')}</td></tr>"
            for e in existing_expenses
        ])
        table_html = f"<table><thead><tr><th>Category</th><th>Amount</th><th>Notes</th></tr></thead><tbody>{rows}</tbody></table>"
        st.markdown(table_html, unsafe_allow_html=True)

    with st.form(key="expense_form"):
        st.markdown("### Enter your expenses")
        expenses = []
        for i in range(5):
            if i < len(existing_expenses):
                amount = existing_expenses[i].get("amount", 0.0)
                category = existing_expenses[i].get("category", "🛍️ Shopping")
                notes = existing_expenses[i].get("notes", "")
            else:
                amount, category, notes = 0.0, "🛍️ Shopping", ""

            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                amount_input = st.number_input(f"Amount #{i+1}", min_value=0.0, step=1.0, value=amount, key=f"amount_{i}")
            with col2:
                category_input = st.selectbox(f"Category #{i+1}", options=categories,
                                              index=categories.index(category) if category in categories else 2,
                                              key=f"category_{i}")
            with col3:
                notes_input = st.text_input(f"Notes #{i+1}", value=notes, key=f"notes_{i}")

            expenses.append({'amount': amount_input, 'category': category_input, 'notes': notes_input})

        if st.form_submit_button("💾 Save Expenses"):
            filtered_expenses = [e for e in expenses if e['amount'] > 0]
            try:
                r = requests.post(f"{API_URL}/expenses/{selected_date}", json=filtered_expenses, timeout=10)
                r.raise_for_status()
                st.success("✅ Expenses updated successfully!")
            except Exception as e:
                st.error(f"❌ Failed to update expenses: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
